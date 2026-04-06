import strawberry
import strawberry_django

from apps.dashboards.models import ExternalDashboard


@strawberry_django.order_type(ExternalDashboard)
class ExternalDashboardOrder:
    page: strawberry.auto
    order: strawberry.auto
    title: strawberry.auto
