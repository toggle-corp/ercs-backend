import strawberry
import strawberry_django

from apps.emergency.models import Emergency


@strawberry_django.filters.filter(Emergency, lookups=True)
class EmergencyFilter:
    id: strawberry.ID | None = strawberry.UNSET
    disaster_type: str | None = strawberry.UNSET
    status: str | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET
    go_id: int | None = strawberry.UNSET
