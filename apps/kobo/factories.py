import datetime

from factory.declarations import LazyAttribute, Sequence
from factory.django import DjangoModelFactory

from apps.kobo.models import VALIDATION_STATUS_APPROVED, KoboForm, KoboSubmission


class KoboSubmissionFactory(DjangoModelFactory[KoboSubmission]):
    form = KoboForm.EMERGENCY_ALERT
    asset_uid = "aydYC8AYCDuX7y4PwfvgrX"
    kobo_id = Sequence(lambda n: n + 1)
    submission_time = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC)
    validation_status = VALIDATION_STATUS_APPROVED
    emergency_code = "EM-20260101-flood-Oromia-zone"
    raw = LazyAttribute(lambda o: {"_id": o.kobo_id})

    class Meta:  # type: ignore[misc]
        model = KoboSubmission
