import strawberry
import strawberry_django
from django.db.models import Q

from apps.emergency.models import Emergency


@strawberry_django.filters.filter(Emergency, lookups=True)
class EmergencyFilter:
    id: strawberry.ID | None = strawberry.UNSET
    disaster_type: str | None = strawberry.UNSET
    status: str | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET
    go_id: int | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(name__icontains=value)
