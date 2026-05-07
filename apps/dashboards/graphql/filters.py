import strawberry
import strawberry_django
from django.db.models import Q

from apps.dashboards.models import CapacityAndResource, ExternalDashboard


@strawberry_django.filters.filter(ExternalDashboard, lookups=True)
class ExternalDashboardFilter:
    id: strawberry.ID | None = strawberry.UNSET
    page: str | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET
    show_on_home: bool | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value) | Q(description__icontains=value)


@strawberry_django.filters.filter(CapacityAndResource, lookups=True)
class CapacityAndResourceFilter:
    id: strawberry.ID | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value) | Q(description__icontains=value)
