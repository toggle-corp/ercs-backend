import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from main.graphql.permissions import IsAuthenticated

from .filters import PmerReportFilter
from .orders import PmerReportOrder
from .types import PmerReportType


@strawberry.type
class Query:
    pmer_reports: OffsetPaginated[PmerReportType] = strawberry_django.offset_paginated(
        filters=PmerReportFilter,
        order=PmerReportOrder,
        permission_classes=[IsAuthenticated],
    )

    pmer_report: PmerReportType = strawberry_django.field(
        permission_classes=[IsAuthenticated],
    )
