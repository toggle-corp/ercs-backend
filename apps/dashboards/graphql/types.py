import strawberry
import strawberry_django

from apps.dashboards.models import CapacityAndResource, CapacityAndResourceIframeUrl, ExternalDashboard


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


@strawberry_django.type(CapacityAndResourceIframeUrl)
class CapacityAndResourceIframeUrlType:
    id: strawberry.ID
    dashboard: ExternalDashboardType
    order: strawberry.auto


@strawberry_django.type(CapacityAndResource)
class CapacityAndResourceType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    region_id: strawberry.ID | None
    is_active: strawberry.auto
    order: strawberry.auto
    iframe_urls: list[CapacityAndResourceIframeUrlType]
    created_by_id: strawberry.ID
    created_at: strawberry.auto
    updated_at: strawberry.auto
