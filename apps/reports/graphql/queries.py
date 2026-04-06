import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import ReportFilter, ThematicAreaFilter
from .orders import ReportOrder
from .types import ReportType, ThematicAreaType


@strawberry.type
class Query:
    thematic_areas: OffsetPaginated[ThematicAreaType] = strawberry_django.offset_paginated(
        filters=ThematicAreaFilter,
    )

    reports: OffsetPaginated[ReportType] = strawberry_django.offset_paginated(
        filters=ReportFilter,
        order=ReportOrder,
    )

    report: ReportType = strawberry_django.field()
