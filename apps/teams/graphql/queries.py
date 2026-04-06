import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from main.graphql.permissions import IsAuthenticated

from .filters import TeamFilter, TeamMemberFilter
from .orders import TeamMemberOrder, TeamOrder
from .types import TeamMemberType, TeamType


@strawberry.type
class Query:
    teams: OffsetPaginated[TeamType] = strawberry_django.offset_paginated(
        filters=TeamFilter,
        order=TeamOrder,
        permission_classes=[IsAuthenticated],
    )

    team: TeamType = strawberry_django.field(
        permission_classes=[IsAuthenticated],
    )

    team_members: OffsetPaginated[TeamMemberType] = strawberry_django.offset_paginated(
        filters=TeamMemberFilter,
        order=TeamMemberOrder,
        permission_classes=[IsAuthenticated],
    )
