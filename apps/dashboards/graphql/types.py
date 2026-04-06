import strawberry
import strawberry_django

from apps.dashboards.models import ExternalDashboard


@strawberry_django.type(ExternalDashboard)
class ExternalDashboardType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    url: strawberry.auto
    page: int
    region_id: strawberry.ID | None
    show_on_home: strawberry.auto
    order: strawberry.auto
    is_active: strawberry.auto
    created_by_id: strawberry.ID
    created_at: strawberry.auto
    updated_at: strawberry.auto
