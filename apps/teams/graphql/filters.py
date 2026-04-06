import strawberry
import strawberry_django

from apps.teams.models import Team, TeamMember


@strawberry_django.filters.filter(Team, lookups=True)
class TeamFilter:
    id: strawberry.ID | None = strawberry.UNSET
    name: str | None = strawberry.UNSET


@strawberry_django.filters.filter(TeamMember, lookups=True)
class TeamMemberFilter:
    id: strawberry.ID | None = strawberry.UNSET
    team_id: strawberry.ID | None = strawberry.UNSET
