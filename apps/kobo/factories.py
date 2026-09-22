from django.utils import timezone
from factory.declarations import LazyAttribute, LazyFunction, Sequence
from factory.django import DjangoModelFactory

from apps.kobo.models import VALIDATION_STATUS_APPROVED, KoboForm, KoboSubmission


class KoboSubmissionFactory(DjangoModelFactory[KoboSubmission]):
    form = KoboForm.EMERGENCY_ALERT
    asset_uid = "aydYC8AYCDuX7y4PwfvgrX"
    kobo_id = Sequence(lambda n: n + 1)
    # Default to "now" so submissions land inside the stats 6-month window; pass an
    # explicit `submission_time` to test the window boundary.
    submission_time = LazyFunction(timezone.now)
    validation_status = VALIDATION_STATUS_APPROVED
    emergency_code = "EM-20260101-flood-Oromia-zone"
    raw = LazyAttribute(lambda o: {"_id": o.kobo_id})

    class Meta:  # type: ignore[misc]
        model = KoboSubmission
