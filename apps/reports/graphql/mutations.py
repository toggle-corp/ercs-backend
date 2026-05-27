import strawberry
import strawberry_django

from apps.reports.models import Link, Report
from apps.reports.serializers import LinkSerializer, ReportSerializer, ThematicAreaSerializer
from main.graphql.context import Info
from main.graphql.permissions import IsAuthenticated, IsStaffOrAbove
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType

from .inputs import LinkCreateInput, LinkUpdateInput, ReportCreateInput, ReportUpdateInput
from .types import LinkType, ReportType, ThematicAreaType


@strawberry.input
class ThematicAreaInput:
    name: str


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def create_thematic_area(
        self,
        info: Info,
        data: ThematicAreaInput,
    ) -> MutationResponseType[ThematicAreaType]:
        return await ModelMutation(ThematicAreaSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def create_report(
        self,
        info: Info,
        data: ReportCreateInput,
    ) -> MutationResponseType[ReportType]:
        return await ModelMutation(ReportSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def update_report(
        self,
        info: Info,
        id: strawberry.ID,
        data: ReportUpdateInput,
    ) -> MutationResponseType[ReportType]:
        instance = await Report.objects.aget(id=id)
        return await ModelMutation(ReportSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def create_link(
        self,
        info: Info,
        data: LinkCreateInput,
    ) -> MutationResponseType[LinkType]:
        return await ModelMutation(LinkSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def update_link(
        self,
        info: Info,
        id: strawberry.ID,
        data: LinkUpdateInput,
    ) -> MutationResponseType[LinkType]:
        instance = await Link.objects.aget(id=id)
        return await ModelMutation(LinkSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def delete_link(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[LinkType]:
        instance = await Link.objects.aget(id=id)
        await instance.adelete()
        return MutationResponseType(ok=True)
