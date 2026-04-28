import strawberry
import strawberry_django

from apps.teams.models import Team, TeamMember


@strawberry_django.type(TeamMember)
class TeamMemberType:
    id: strawberry.ID
    team_id: strawberry.ID
    name: strawberry.auto
    position: strawberry.auto
    email: strawberry.auto
    phone_number: strawberry.auto
    sex: int | None
    region_id: strawberry.ID | None
    woreda_id: strawberry.ID | None
    training: strawberry.auto
    field_of_study: strawberry.auto
    order: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto


@strawberry_django.type(Team)
class TeamType:
    id: strawberry.ID
    name: strawberry.auto
    description: strawberry.auto
    members: list[TeamMemberType]
    created_at: strawberry.auto
    updated_at: strawberry.auto
