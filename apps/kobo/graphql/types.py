import datetime
from typing import Any

import strawberry
import strawberry_django
from strawberry.scalars import JSON

from apps.kobo.models import VALIDATION_STATUS_APPROVED, KoboForm, KoboSubmission


def _raw_int(raw: dict[str, Any], key: str) -> int | None:
    try:
        return int(float(raw.get(key)))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


@strawberry_django.type(KoboSubmission)
class KoboSubmissionType:
    id: strawberry.ID
    form: int
    asset_uid: strawberry.auto
    kobo_id: strawberry.auto
    submission_time: strawberry.auto
    validation_status: strawberry.auto
    emergency_code: strawberry.auto
    region_id: strawberry.ID | None
    raw: JSON
    created_at: strawberry.auto
    updated_at: strawberry.auto

    @strawberry.field
    def form_display(self) -> str:
        return self.get_form_display()  # type: ignore[attr-defined]


@strawberry_django.type(KoboSubmission)
class KoboEmergencyType:
    """An ERCS Kobo Emergency Alert, shaped for the emergencies list.

    Scoped to approved Emergency Alert submissions (see get_queryset); the
    display fields are derived from the raw Kobo record.
    """

    id: strawberry.ID
    kobo_id: strawberry.auto
    submission_time: strawberry.auto
    emergency_code: strawberry.auto
    region_id: strawberry.ID | None

    @classmethod
    def get_queryset(cls, queryset: Any, info: Any, **kwargs: Any) -> Any:
        return queryset.filter(
            form=KoboForm.EMERGENCY_ALERT,
            validation_status=VALIDATION_STATUS_APPROVED,
        )

    # `only=["raw"]` tells the optimizer to load the raw column, otherwise it is
    # deferred and `self.raw` triggers a lazy DB fetch in the async resolver.
    @strawberry_django.field(only=["raw"])
    def hazard(self) -> str | None:
        return self.raw.get("context/hazard")  # type: ignore[attr-defined]

    @strawberry_django.field(only=["raw"])
    def alert_type(self) -> str | None:
        return self.raw.get("context/alert-type")  # type: ignore[attr-defined]

    @strawberry_django.field(only=["raw"])
    def region(self) -> str | None:
        return self.raw.get("geo/region-one")  # type: ignore[attr-defined]

    @strawberry_django.field(only=["raw"])
    def location_scope(self) -> str | None:
        return self.raw.get("geo/location_scope")  # type: ignore[attr-defined]

    @strawberry_django.field(only=["raw"])
    def start_date(self) -> str | None:
        return self.raw.get("context/start_date")  # type: ignore[attr-defined]

    @strawberry_django.field(only=["raw"])
    def people_affected(self) -> int | None:
        return _raw_int(self.raw, "ppl_impact_group/ppl_affected")  # type: ignore[attr-defined]

    @strawberry_django.field(only=["raw"])
    def people_displaced(self) -> int | None:
        return _raw_int(self.raw, "ppl_impact_group/ppl_affected_displaced")  # type: ignore[attr-defined]


# --------------------------------------------------------------------------
# Stats types (computed aggregates — not model-backed)
# --------------------------------------------------------------------------


@strawberry.type
class KeyCount:
    """A category and how many submissions fall in it (e.g. hazard → count)."""

    key: str
    count: int


@strawberry.type
class KoboSource:
    """Provenance + freshness for a single form's stats."""

    form: int
    form_label: str
    asset_uid: str
    last_fetched_at: datetime.datetime | None
    last_status: str
    total_records: int
    confirmed_records: int


@strawberry.type
class AlertStats:
    source: KoboSource
    total_emergencies: int
    people_affected: int
    people_displaced: int
    deaths: int
    injured: int
    missing: int
    by_hazard: list[KeyCount]
    by_region: list[KeyCount]


@strawberry.type
class RapidNeedsStats:
    source: KoboSource
    total_assessments: int
    people_in_need: int
    people_affected: int
    people_displaced: int
    top_priority_sectors: list[KeyCount]
    by_region: list[KeyCount]


@strawberry.type
class FieldStats:
    source: KoboSource
    total_reports: int
    people_reached: int
    staff_mobilized: int
    volunteers_mobilized: int
    bdrt_mobilized: int
    ambulances_mobilized: int
    support_requested: int
    by_region: list[KeyCount]


@strawberry.type
class KoboStats:
    """Key stats across the three confirmed EOC forms, each with its source
    (form + asset uid) and last-fetched date.
    """

    generated_at: datetime.datetime
    alert: AlertStats
    rapid_needs: RapidNeedsStats
    field: FieldStats
