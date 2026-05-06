import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import ResourceFilter
from .orders import ResourceOrder
from .types import ResourceType


@strawberry.type
class Query:
    resources: OffsetPaginated[ResourceType] = strawberry_django.offset_paginated(
        filters=ResourceFilter,
        order=ResourceOrder,
    )

    resource: ResourceType = strawberry_django.field()
