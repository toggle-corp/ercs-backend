import typing

import strawberry
import strawberry_django

from apps.teams.models import Team, TeamMember


@strawberry_django.filters.filter(Team, lookups=True)
class TeamFilter:
    id: strawberry.ID | None = strawberry.UNSET
    name: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, queryset: typing.Any, value: str, prefix: str) -> typing.Any:
        return queryset.filter(name__icontains=value)


@strawberry_django.filters.filter(TeamMember, lookups=True)
class TeamMemberFilter:
    id: strawberry.ID | None = strawberry.UNSET
    team_id: strawberry.ID | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET
    woreda_id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, queryset: typing.Any, value: str, prefix: str) -> typing.Any:
        return queryset.filter(name__icontains=value)
