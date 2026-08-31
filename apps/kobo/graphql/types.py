import datetime

import strawberry
import strawberry_django
from strawberry.scalars import JSON

from apps.kobo.models import KoboSubmission


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
