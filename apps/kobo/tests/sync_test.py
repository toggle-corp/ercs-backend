"""Cover the destructive half of the sync: the prune and its guards."""

from typing import Any
from unittest import mock

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from apps.kobo.factories import KoboSubmissionFactory
from apps.kobo.models import KoboForm, KoboSubmission, KoboSyncState
from apps.kobo.sync import FORM_SPECS, KoboConfigError, KoboSyncer
from main.tests import TestCase

ALERT_SPEC = FORM_SPECS[0]


def _record(kobo_id: int, **extra: Any) -> dict[str, Any]:
    return {
        "_id": kobo_id,
        "_submission_time": "2026-08-27T10:00:00",
        "_validation_status": {"uid": "validation_status_approved"},
        "emergency_code/unique_code": f"EM-{kobo_id}",
        **extra,
    }


@override_settings(KOBO_ACCESS_TOKEN="test-token")
class TestReconcile(TestCase):
    def _sync(self, records: list[dict[str, Any]], **kwargs: Any):
        syncer = KoboSyncer()
        with mock.patch.object(KoboSyncer, "_fetch_all", return_value=iter(records)):
            return syncer.sync_form(ALERT_SPEC, **kwargs)

    def test_upsert_and_prune(self):
        KoboSubmissionFactory.create(form=KoboForm.EMERGENCY_ALERT, asset_uid=ALERT_SPEC.asset_uid, kobo_id=1)
        KoboSubmissionFactory.create(form=KoboForm.EMERGENCY_ALERT, asset_uid=ALERT_SPEC.asset_uid, kobo_id=2)

        result = self._sync([_record(1), _record(3)])

        assert result.ok
        assert (result.created, result.updated, result.deleted) == (1, 1, 1)
        assert set(KoboSubmission.objects.values_list("kobo_id", flat=True)) == {1, 3}

    def test_prune_is_scoped_by_form_not_asset_uid(self):
        """Rows left behind by a previously configured asset must go too.

        The stats layer reads by ``form``, so a stale asset's rows would be
        counted alongside the current asset's.
        """
        KoboSubmissionFactory.create(form=KoboForm.EMERGENCY_ALERT, asset_uid="oldAssetUid", kobo_id=1)
        # Another form's rows are untouched by this form's reconcile.
        KoboSubmissionFactory.create(form=KoboForm.EMERGENCY_FIELD, asset_uid="fieldAssetUid", kobo_id=1)

        result = self._sync([_record(1)])

        assert result.deleted == 1
        assert not KoboSubmission.objects.filter(asset_uid="oldAssetUid").exists()
        assert KoboSubmission.objects.filter(form=KoboForm.EMERGENCY_FIELD).count() == 1
        assert KoboSubmission.objects.filter(form=KoboForm.EMERGENCY_ALERT).count() == 1

    def test_empty_response_does_not_prune(self):
        KoboSubmissionFactory.create(form=KoboForm.EMERGENCY_ALERT, asset_uid=ALERT_SPEC.asset_uid, kobo_id=1)

        result = self._sync([])

        assert not result.ok
        assert "refusing to prune" in result.error
        assert KoboSubmission.objects.filter(form=KoboForm.EMERGENCY_ALERT).count() == 1
        state = KoboSyncState.objects.get(form=KoboForm.EMERGENCY_ALERT)
        assert state.last_status == KoboSyncState.Status.FAILURE
        assert state.last_fetched_at is None

    def test_empty_response_is_fine_when_nothing_is_stored(self):
        result = self._sync([])

        assert result.ok
        assert result.total == 0

    def test_missing_submission_time_is_still_mirrored(self):
        result = self._sync([_record(1) | {"_submission_time": None}])

        assert result.ok
        assert KoboSubmission.objects.get(kobo_id=1).submission_time is None

    def test_dry_run_writes_nothing(self):
        KoboSubmissionFactory.create(form=KoboForm.EMERGENCY_ALERT, asset_uid=ALERT_SPEC.asset_uid, kobo_id=1)

        result = self._sync([_record(2)], dry_run=True)

        assert result.ok
        assert set(KoboSubmission.objects.values_list("kobo_id", flat=True)) == {1}
        assert not KoboSyncState.objects.exists()

    def test_dry_run_writes_nothing_on_failure(self):
        syncer = KoboSyncer()
        with mock.patch.object(KoboSyncer, "_fetch_all", side_effect=RuntimeError("boom")):
            result = syncer.sync_form(ALERT_SPEC, dry_run=True)

        assert not result.ok
        assert not KoboSyncState.objects.exists()

    def test_fetch_failure_keeps_existing_rows(self):
        KoboSubmissionFactory.create(form=KoboForm.EMERGENCY_ALERT, asset_uid=ALERT_SPEC.asset_uid, kobo_id=1)

        syncer = KoboSyncer()
        with mock.patch.object(KoboSyncer, "_fetch_all", side_effect=RuntimeError("boom")):
            result = syncer.sync_form(ALERT_SPEC)

        assert not result.ok
        assert KoboSubmission.objects.count() == 1
        assert KoboSyncState.objects.get(form=KoboForm.EMERGENCY_ALERT).last_status == KoboSyncState.Status.FAILURE


@override_settings(KOBO_ACCESS_TOKEN=None)
class TestMissingToken(TestCase):
    """Without a token no form can succeed, so the run must abort up front rather
    than fail each form in turn.
    """

    def test_run_raises_before_touching_anything(self):
        KoboSubmissionFactory.create(form=KoboForm.EMERGENCY_ALERT, asset_uid=ALERT_SPEC.asset_uid, kobo_id=1)

        with pytest.raises(KoboConfigError, match="KOBO_ACCESS_TOKEN"):
            KoboSyncer().run()

        # No FAILURE rows written, no data touched.
        assert not KoboSyncState.objects.exists()
        assert KoboSubmission.objects.count() == 1

    def test_command_reports_a_clean_error(self):
        with pytest.raises(CommandError, match="KOBO_ACCESS_TOKEN is not configured"):
            call_command("sync_kobo")

        assert not KoboSyncState.objects.exists()

    def test_dry_run_also_fails_fast(self):
        with pytest.raises(CommandError, match="KOBO_ACCESS_TOKEN"):
            call_command("sync_kobo", "--dry-run")
