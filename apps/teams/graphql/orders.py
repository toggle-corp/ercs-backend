import strawberry
import strawberry_django

from apps.teams.models import Team, TeamMember


@strawberry_django.order_type(Team)
class TeamOrder:
    name: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.order_type(TeamMember)
class TeamMemberOrder:
    order: strawberry.auto
    name: strawberry.auto
