import strawberry
import strawberry_django

from apps.pmer.models import PmerReport
from apps.pmer.serializers import PmerReportSerializer
from main.graphql.context import Info
from main.graphql.permissions import IsAuthenticated
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType

from .inputs import PmerReportCreateInput, PmerReportUpdateInput
from .types import PmerReportType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def create_pmer_report(
        self,
        info: Info,
        data: PmerReportCreateInput,
    ) -> MutationResponseType[PmerReportType]:
        return await ModelMutation(PmerReportSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def update_pmer_report(
        self,
        info: Info,
        id: strawberry.ID,
        data: PmerReportUpdateInput,
    ) -> MutationResponseType[PmerReportType]:
        instance = await PmerReport.objects.aget(id=id)
        return await ModelMutation(PmerReportSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def delete_pmer_report(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[PmerReportType]:
        instance = await PmerReport.objects.aget(id=id)
        await instance.adelete()
        return MutationResponseType(ok=True)
