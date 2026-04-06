import strawberry
import strawberry_django

from apps.dashboards.models import ExternalDashboard


@strawberry_django.filters.filter(ExternalDashboard, lookups=True)
class ExternalDashboardFilter:
    id: strawberry.ID | None = strawberry.UNSET
    page: str | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET
    show_on_home: bool | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET
