import strawberry
import strawberry_django

from apps.dashboards.models import CapacityAndResource, ExternalDashboard
from apps.dashboards.serializers import CapacityAndResourceSerializer, ExternalDashboardSerializer
from main.graphql.context import Info
from main.graphql.permissions import IsStaffOrAbove
from utils.graphql.drf import MutationCustomErrorType
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType

from .inputs import (
    CapacityAndResourceCreateInput,
    CapacityAndResourceUpdateInput,
    ExternalDashboardCreateInput,
    ExternalDashboardUpdateInput,
)
from .types import CapacityAndResourceType, ExternalDashboardType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def create_external_dashboard(
        self,
        info: Info,
        data: ExternalDashboardCreateInput,
    ) -> MutationResponseType[ExternalDashboardType]:
        return await ModelMutation(ExternalDashboardSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def update_external_dashboard(
        self,
        info: Info,
        id: strawberry.ID,
        data: ExternalDashboardUpdateInput,
    ) -> MutationResponseType[ExternalDashboardType]:
        instance = await ExternalDashboard.objects.aget(id=id)
        return await ModelMutation(ExternalDashboardSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def create_capacity_and_resource(
        self,
        info: Info,
        data: CapacityAndResourceCreateInput,
    ) -> MutationResponseType[CapacityAndResourceType]:
        return await ModelMutation(CapacityAndResourceSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def update_capacity_and_resource(
        self,
        info: Info,
        id: strawberry.ID,
        data: CapacityAndResourceUpdateInput,
    ) -> MutationResponseType[CapacityAndResourceType]:
        instance = await CapacityAndResource.objects.aget(id=id)
        return await ModelMutation(CapacityAndResourceSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def add_dashboard_to_home(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[ExternalDashboardType]:
        instance = await ExternalDashboard.objects.aget(id=id)
        if instance.show_on_home:
            return MutationResponseType(result=instance)  # type: ignore[reportAttributeAccessIssue]

        count = await ExternalDashboard.objects.filter(show_on_home=True).acount()
        if count >= ExternalDashboardSerializer.HOME_DASHBOARD_LIMIT:
            return MutationResponseType(
                ok=False,
                errors=MutationCustomErrorType.generate_message(
                    f"Maximum of {ExternalDashboardSerializer.HOME_DASHBOARD_LIMIT} dashboards "
                    "can be shown on the home page.",
                ),
            )
        instance.show_on_home = True
        await instance.asave(update_fields=["show_on_home"])
        return MutationResponseType(result=instance)  # type: ignore[reportAttributeAccessIssue]

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def remove_dashboard_from_home(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[ExternalDashboardType]:
        instance = await ExternalDashboard.objects.aget(id=id)
        instance.show_on_home = False
        await instance.asave(update_fields=["show_on_home"])
        return MutationResponseType(result=instance)  # type: ignore[reportAttributeAccessIssue]

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def delete_external_dashboard(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[ExternalDashboardType]:
        instance = await ExternalDashboard.objects.aget(id=id)
        await instance.adelete()
        return MutationResponseType(ok=True)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAbove])
    async def delete_capacity_and_resource(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[CapacityAndResourceType]:
        instance = await CapacityAndResource.objects.aget(id=id)
        await instance.adelete()
        return MutationResponseType(ok=True)
