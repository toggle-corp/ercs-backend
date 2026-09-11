import strawberry
import strawberry_django

from apps.teams.models import Team, TeamMember
from apps.teams.serializers import TeamMemberSerializer, TeamSerializer
from main.graphql.context import Info
from main.graphql.permissions import IsStaffOrAboveDelete, IsStaffOrAboveMutation
from utils.graphql.mutations import ModelMutation, handle_delete_mutation
from utils.graphql.types import DeleteMutationResponseType, MutationResponseType

from .inputs import (
    TeamCreateInput,
    TeamMemberBulkCreateInput,
    TeamMemberCreateInput,
    TeamMemberUpdateInput,
    TeamUpdateInput,
)
from .types import TeamMemberType, TeamType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def create_team(
        self,
        info: Info,
        data: TeamCreateInput,
    ) -> MutationResponseType[TeamType]:
        return await ModelMutation(TeamSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def update_team(
        self,
        info: Info,
        id: strawberry.ID,
        data: TeamUpdateInput,
    ) -> MutationResponseType[TeamType]:
        instance = await Team.objects.aget(id=id)
        return await ModelMutation(TeamSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def create_team_member(
        self,
        info: Info,
        data: TeamMemberCreateInput,
    ) -> MutationResponseType[TeamMemberType]:
        return await ModelMutation(TeamMemberSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def update_team_member(
        self,
        info: Info,
        id: strawberry.ID,
        data: TeamMemberUpdateInput,
    ) -> MutationResponseType[TeamMemberType]:
        instance = await TeamMember.objects.aget(id=id)
        return await ModelMutation(TeamMemberSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveDelete], handle_django_errors=False)
    async def delete_team_member(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> DeleteMutationResponseType:
        return await handle_delete_mutation(TeamMember, id=id)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveDelete], handle_django_errors=False)
    async def delete_team(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> DeleteMutationResponseType:
        return await handle_delete_mutation(Team, id=id)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def bulk_create_team_members(
        self,
        info: Info,
        data: TeamMemberBulkCreateInput,
    ) -> MutationResponseType[list[TeamMemberType]]:
        return await ModelMutation(TeamMemberSerializer).handle_bulk_create_mutation(data.members, info)
