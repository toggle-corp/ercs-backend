import strawberry
import strawberry_django

from apps.dashboards.models import CapacityAndResource, ExternalDashboard


@strawberry_django.order_type(ExternalDashboard)
class ExternalDashboardOrder:
    page: strawberry.auto
    order: strawberry.auto
    title: strawberry.auto


@strawberry_django.order_type(CapacityAndResource)
class CapacityAndResourceOrder:
    order: strawberry.auto
    title: strawberry.auto
