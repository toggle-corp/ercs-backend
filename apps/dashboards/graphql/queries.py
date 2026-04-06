import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import ExternalDashboardFilter
from .orders import ExternalDashboardOrder
from .types import ExternalDashboardType


@strawberry.type
class Query:
    external_dashboards: OffsetPaginated[ExternalDashboardType] = strawberry_django.offset_paginated(
        filters=ExternalDashboardFilter,
        order=ExternalDashboardOrder,
    )

    external_dashboard: ExternalDashboardType = strawberry_django.field()
