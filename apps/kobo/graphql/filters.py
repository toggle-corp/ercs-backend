import strawberry
import strawberry_django
from django.db.models import Q

from apps.kobo.models import KoboSubmission


@strawberry_django.filters.filter(KoboSubmission, lookups=True)
class KoboSubmissionFilter:
    id: strawberry.ID | None = strawberry.UNSET
    form: int | None = strawberry.UNSET
    validation_status: str | None = strawberry.UNSET
    emergency_code: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def regions(self, value: list[strawberry.ID], prefix: str) -> Q:
        return Q(region_id__in=value)
