import strawberry
import strawberry_django

from apps.dashboards.models import CapacityAndResource, DashboardPage


@strawberry.input
class ExternalDashboardCreateInput:
    title: str
    url: str
    page: DashboardPage
    description: str | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    capacity_and_resource: strawberry.ID | None = strawberry.UNSET
    show_on_home: bool = False
    order: int = 0
    is_active: bool = True


@strawberry.input
class ExternalDashboardOrderInput:
    id: strawberry.ID
    order: int


@strawberry.input
class ExternalDashboardUpdateInput:
    title: str | None = strawberry.UNSET
    url: str | None = strawberry.UNSET
    page: DashboardPage | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    capacity_and_resource: strawberry.ID | None = strawberry.UNSET
    show_on_home: bool | None = strawberry.UNSET
    order: int | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET


@strawberry_django.input(CapacityAndResource)
class CapacityAndResourceCreateInput:
    title: strawberry.auto
    description: strawberry.auto
    region: strawberry.ID | None = strawberry.UNSET
    is_active: strawberry.auto
    order: int


@strawberry_django.partial(CapacityAndResource)
class CapacityAndResourceUpdateInput:
    title: strawberry.auto
    description: strawberry.auto
    is_active: strawberry.auto
    order: strawberry.auto
    region: strawberry.ID | None = strawberry.UNSET
