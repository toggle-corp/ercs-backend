import strawberry
import strawberry_django

from apps.teams.models import Team, TeamMember
from apps.teams.serializers import TeamMemberSerializer, TeamSerializer
from main.graphql.context import Info
from main.graphql.permissions import IsStaffOrAbove
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType

from .inputs import (
    TeamCreateInput,
    TeamMemberCreateInput,
    TeamMemberUpdateInput,
    TeamUpdateInput,
)
from .types import TeamMemberType, TeamType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def create_team(
        self,
        info: Info,
        data: TeamCreateInput,
    ) -> MutationResponseType[TeamType]:
        return await ModelMutation(TeamSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def update_team(
        self,
        info: Info,
        id: strawberry.ID,
        data: TeamUpdateInput,
    ) -> MutationResponseType[TeamType]:
        instance = await Team.objects.aget(id=id)
        return await ModelMutation(TeamSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def create_team_member(
        self,
        info: Info,
        data: TeamMemberCreateInput,
    ) -> MutationResponseType[TeamMemberType]:
        return await ModelMutation(TeamMemberSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def update_team_member(
        self,
        info: Info,
        id: strawberry.ID,
        data: TeamMemberUpdateInput,
    ) -> MutationResponseType[TeamMemberType]:
        instance = await TeamMember.objects.aget(id=id)
        return await ModelMutation(TeamMemberSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def delete_team_member(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[TeamMemberType]:
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _delete() -> MutationResponseType:
            try:
                obj = TeamMember.objects.get(id=id)
                obj.delete()
                return MutationResponseType(ok=True)
            except TeamMember.DoesNotExist:
                return MutationResponseType(ok=False)

        return await _delete()

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def delete_team(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[TeamType]:
        instance = await Team.objects.aget(id=id)
        await instance.adelete()
        return MutationResponseType(ok=True)
