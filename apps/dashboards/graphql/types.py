import strawberry
import strawberry_django

from apps.dashboards.models import CapacityAndResource, DashboardPage, ExternalDashboard


@strawberry_django.type(ExternalDashboard)
class ExternalDashboardType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    url: strawberry.auto
    page: DashboardPage
    region_id: strawberry.ID | None
    capacity_and_resource_id: strawberry.ID | None
    show_on_home: strawberry.auto
    order: strawberry.auto
    is_active: strawberry.auto
    created_by_id: strawberry.ID
    created_at: strawberry.auto
    updated_at: strawberry.auto

    @strawberry.field
    def page_display(self) -> str:
        return self.get_page_display()  # type: ignore[reportAttributeAccessIssue]


@strawberry_django.type(CapacityAndResource)
class CapacityAndResourceType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    region_id: strawberry.ID | None
    is_active: strawberry.auto
    order: strawberry.auto
    dashboards: list[ExternalDashboardType]
    created_by_id: strawberry.ID

    @strawberry.field
    def dashboards_count(self) -> int:
        return self.dashboards.count()  # type: ignore[reportAttributeAccessIssue]

    created_at: strawberry.auto
    updated_at: strawberry.auto
