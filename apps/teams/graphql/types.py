import strawberry
import strawberry_django
from asgiref.sync import sync_to_async

from apps.teams.models import Team, TeamMember, TeamMemberSex


@strawberry_django.type(TeamMember)
class TeamMemberType:
    id: strawberry.ID
    team_id: strawberry.ID
    name: strawberry.auto
    position: strawberry.auto
    email: strawberry.auto
    phone_number: strawberry.auto
    sex: TeamMemberSex | None

    @strawberry.field
    def sex_display(self) -> str | None:
        if self.sex is None:
            return None
        return self.get_sex_display()  # type: ignore[reportAttributeAccessIssue]

    @strawberry.field
    @sync_to_async
    def region(self) -> strawberry.ID | None:
        return self.region_id  # type: ignore[reportAttributeAccessIssue]

    @strawberry.field
    @sync_to_async
    def woreda(self) -> strawberry.ID | None:
        return self.woreda_id  # type: ignore[reportAttributeAccessIssue]

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
