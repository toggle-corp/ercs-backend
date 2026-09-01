"""Fetch ERCS EOC Kobo submissions and reconcile them into the local store.

Design (see ``backend/docs/kobo-api.md`` and the ADR-style notes below):

- **Three confirmed forms** — Alert, RNA, Field — pulled with ``KOBO_ACCESS_TOKEN``.
- **Fetch-before-mutate**: every submission is downloaded first; only then do we
  touch the DB, so a failed/partial fetch never wipes good data.
- **Reconcile, not additive**: within one transaction per form we upsert each
  record by ``(asset_uid, kobo_id)`` and prune stored rows whose ``kobo_id`` is
  no longer present in Kobo. A row's UUID pk + ``created_at`` survive across runs.
- **Per-form isolation**: one form failing is logged (and reported to Sentry) but
  does not block the others; that form keeps its previous data.
- **Store all rows**: ``validation_status`` is kept per row so the stats layer can
  filter to approved submissions.
"""

import datetime
import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any

import requests
import sentry_sdk
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.geo.models import AdminArea, AdminAreaLevel
from apps.kobo.models import KoboForm, KoboSubmission, KoboSyncState

logger = logging.getLogger(__name__)

HTTP_TIMEOUT = 60.0
PAGE_LIMIT = 2000


@dataclass(frozen=True)
class FormSpec:
    """Where a form lives and how to derive its promoted columns from a record."""

    form: KoboForm
    asset_uid: str
    # First present key wins — used to derive the promoted `emergency_code` column.
    emergency_code_keys: tuple[str, ...]
    # First present key wins — the reporting region name, matched to an AdminArea.
    region_keys: tuple[str, ...]


FORM_SPECS: tuple[FormSpec, ...] = (
    FormSpec(
        form=KoboForm.EMERGENCY_ALERT,
        asset_uid="aydYC8AYCDuX7y4PwfvgrX",
        emergency_code_keys=("emergency_code/unique_code",),
        region_keys=("geo/region-one",),
    ),
    FormSpec(
        form=KoboForm.RAPID_NEEDS_ASSESSMENT,
        asset_uid="aPuV7tDb9mdRiK8hUhkxJC",
        emergency_code_keys=("context/emergency-selection", "location/alert_code"),
        region_keys=("location/region",),
    ),
    FormSpec(
        form=KoboForm.EMERGENCY_FIELD,
        asset_uid="aby6sxp4DyEiohs4XMn7Mu",
        emergency_code_keys=("context/emergency-selection", "location/alert_code"),
        region_keys=("location/region-one",),
    ),
)


@dataclass
class FormResult:
    form: KoboForm
    ok: bool
    created: int = 0
    updated: int = 0
    deleted: int = 0
    total: int = 0
    error: str = ""


@dataclass
class KoboSyncer:
    """Fetches and reconciles Kobo submissions. Safe to run repeatedly."""

    stdout: Any = None
    style: Any = None
    _region_cache: dict[str, AdminArea] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Case-insensitive, underscore-insensitive lookup of REGION admin areas.
        for area in AdminArea.objects.filter(level=AdminAreaLevel.REGION):
            self._region_cache[self._normalize_region(area.name)] = area

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self, dry_run: bool = False, only: KoboForm | None = None) -> list[FormResult]:
        results: list[FormResult] = []
        for spec in FORM_SPECS:
            if only is not None and spec.form != only:
                continue
            results.append(self.sync_form(spec, dry_run=dry_run))
        return results

    def sync_form(self, spec: FormSpec, dry_run: bool = False) -> FormResult:
        label = KoboForm(spec.form).label
        try:
            records = list(self._fetch_all(spec.asset_uid))  # network first, before any DB write
        except Exception as exc:
            sentry_sdk.capture_exception(exc)
            logger.exception("Kobo fetch failed for %s (%s)", label, spec.asset_uid)
            self._record_state(spec, ok=False, error=str(exc), count=None)
            self._warn(f"  {label}: FETCH FAILED — {exc} (existing rows kept)")
            return FormResult(form=spec.form, ok=False, error=str(exc))

        try:
            with transaction.atomic():
                result = self._reconcile(spec, records)
                if dry_run:
                    transaction.set_rollback(True)
                else:
                    self._record_state(spec, ok=True, error="", count=result.total)
        except Exception as exc:
            sentry_sdk.capture_exception(exc)
            logger.exception("Kobo reconcile failed for %s", label)
            self._record_state(spec, ok=False, error=str(exc), count=None)
            self._warn(f"  {label}: RECONCILE FAILED — {exc} (existing rows kept)")
            return FormResult(form=spec.form, ok=False, error=str(exc))

        self._ok(
            f"  {label}: {result.created} created, {result.updated} updated, "
            f"{result.deleted} pruned ({result.total} total)" + (" [dry-run rolled back]" if dry_run else ""),
        )
        return result

    # ------------------------------------------------------------------
    # Reconcile
    # ------------------------------------------------------------------

    def _reconcile(self, spec: FormSpec, records: list[dict[str, Any]]) -> FormResult:
        created = updated = 0
        seen: set[int] = set()

        for rec in records:
            kobo_id = int(rec["_id"])
            seen.add(kobo_id)
            _, was_created = KoboSubmission.objects.update_or_create(
                asset_uid=spec.asset_uid,
                kobo_id=kobo_id,
                defaults={
                    "form": spec.form,
                    "submission_time": self._parse_dt(rec.get("_submission_time")),
                    "validation_status": (rec.get("_validation_status") or {}).get("uid", "") or "",
                    "emergency_code": self._first(rec, spec.emergency_code_keys),
                    "region": self._match_region(self._first(rec, spec.region_keys)),
                    "raw": rec,
                },
            )
            created += was_created
            updated += not was_created

        deleted, _ = KoboSubmission.objects.filter(asset_uid=spec.asset_uid).exclude(kobo_id__in=seen).delete()
        return FormResult(
            form=spec.form,
            ok=True,
            created=created,
            updated=updated,
            deleted=deleted,
            total=len(seen),
        )

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def _fetch_all(self, asset_uid: str) -> Iterator[dict[str, Any]]:
        token = settings.KOBO_ACCESS_TOKEN
        if not token:
            raise RuntimeError("KOBO_ACCESS_TOKEN is not configured.")
        headers = {"Authorization": f"Token {token}"}
        url: str | None = f"{settings.KOBO_DOMAIN}/api/v2/assets/{asset_uid}/data/?format=json&limit={PAGE_LIMIT}"
        while url:
            resp = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            yield from data["results"]
            url = data.get("next")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_dt(value: Any) -> datetime.datetime | None:
        """Kobo `_submission_time` is naive UTC; return a tz-aware datetime."""
        if not value:
            return None
        dt = parse_datetime(str(value))
        if dt is not None and timezone.is_naive(dt):
            dt = timezone.make_aware(dt, datetime.UTC)
        return dt

    @staticmethod
    def _first(rec: dict[str, Any], keys: tuple[str, ...]) -> str | None:
        for key in keys:
            value = rec.get(key)
            if value:
                return str(value)
        return None

    @staticmethod
    def _normalize_region(name: str | None) -> str:
        return (name or "").replace("_", " ").strip().casefold()

    def _match_region(self, name: str | None) -> AdminArea | None:
        if not name:
            return None
        area = self._region_cache.get(self._normalize_region(name))
        if area is None:
            logger.warning("Kobo sync: no AdminArea REGION match for %r", name)
        return area

    def _record_state(self, spec: FormSpec, ok: bool, error: str, count: int | None) -> None:
        defaults: dict[str, Any] = {
            "asset_uid": spec.asset_uid,
            "last_status": KoboSyncState.Status.SUCCESS if ok else KoboSyncState.Status.FAILURE,
            "last_error": error,
        }
        if ok:
            defaults["last_fetched_at"] = timezone.now()
            defaults["record_count"] = count or 0
        KoboSyncState.objects.update_or_create(form=spec.form, defaults=defaults)

    def _ok(self, msg: str) -> None:
        logger.info(msg)
        if self.stdout is not None:
            self.stdout.write(self.style.SUCCESS(msg) if self.style else msg)

    def _warn(self, msg: str) -> None:
        logger.warning(msg)
        if self.stdout is not None:
            self.stdout.write(self.style.WARNING(msg) if self.style else msg)
