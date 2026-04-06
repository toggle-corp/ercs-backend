import strawberry


@strawberry.input
class TeamCreateInput:
    name: str
    description: str | None = strawberry.UNSET


@strawberry.input
class TeamUpdateInput:
    name: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET


@strawberry.input
class TeamMemberCreateInput:
    team: strawberry.ID
    name: str
    position: str
    email: str | None = strawberry.UNSET
    phone_number: str | None = strawberry.UNSET
    order: int = 0


@strawberry.input
class TeamMemberUpdateInput:
    team: strawberry.ID | None = strawberry.UNSET
    name: str | None = strawberry.UNSET
    position: str | None = strawberry.UNSET
    email: str | None = strawberry.UNSET
    phone_number: str | None = strawberry.UNSET
    order: int | None = strawberry.UNSET
