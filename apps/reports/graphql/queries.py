import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from main.graphql.permissions import IsAuthenticated

from .filters import LinkFilter, ReportFilter, ThematicAreaFilter
from .orders import LinkOrder, ReportOrder
from .types import LinkType, ReportType, ThematicAreaType


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

    public_links: OffsetPaginated[LinkType] = strawberry_django.offset_paginated(
        filters=LinkFilter,
        order=LinkOrder,
    )

    internal_links: OffsetPaginated[LinkType] = strawberry_django.offset_paginated(
        filters=LinkFilter,
        order=LinkOrder,
        permission_classes=[IsAuthenticated],
    )

    link: LinkType = strawberry_django.field()
