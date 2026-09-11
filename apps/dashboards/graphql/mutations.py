import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from django.db import transaction

from apps.dashboards.models import CapacityAndResource, ExternalDashboard
from apps.dashboards.serializers import CapacityAndResourceSerializer, ExternalDashboardSerializer
from main.graphql.context import Info
from main.graphql.permissions import IsStaffOrAboveDelete, IsStaffOrAboveMutation
from utils.graphql.drf import MutationCustomErrorType
from utils.graphql.mutations import ModelMutation, handle_delete_mutation
from utils.graphql.types import CustomErrorType, DeleteMutationResponseType, MutationResponseType

from .inputs import (
    CapacityAndResourceCreateInput,
    CapacityAndResourceUpdateInput,
    ExternalDashboardCreateInput,
    ExternalDashboardOrderInput,
    ExternalDashboardUpdateInput,
)
from .types import CapacityAndResourceType, ExternalDashboardType


@sync_to_async
def _bulk_update_external_dashboard_order(
    order_by_id: dict[str, int],
) -> tuple[CustomErrorType | None, list[ExternalDashboard] | None]:
    with transaction.atomic():
        dashboards = list(ExternalDashboard.objects.filter(id__in=order_by_id))
        if len(dashboards) != len(order_by_id):
            return MutationCustomErrorType.generate_message("One or more dashboards were not found."), None
        for dashboard in dashboards:
            dashboard.order = order_by_id[str(dashboard.pk)]
        ExternalDashboard.objects.bulk_update(dashboards, ["order"])
    dashboards.sort(key=lambda dashboard: (dashboard.page, dashboard.order))
    return None, dashboards


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def create_external_dashboard(
        self,
        info: Info,
        data: ExternalDashboardCreateInput,
    ) -> MutationResponseType[ExternalDashboardType]:
        return await ModelMutation(ExternalDashboardSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def update_external_dashboard(
        self,
        info: Info,
        id: strawberry.ID,
        data: ExternalDashboardUpdateInput,
    ) -> MutationResponseType[ExternalDashboardType]:
        instance = await ExternalDashboard.objects.aget(id=id)
        return await ModelMutation(ExternalDashboardSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def create_capacity_and_resource(
        self,
        info: Info,
        data: CapacityAndResourceCreateInput,
    ) -> MutationResponseType[CapacityAndResourceType]:
        return await ModelMutation(CapacityAndResourceSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def update_capacity_and_resource(
        self,
        info: Info,
        id: strawberry.ID,
        data: CapacityAndResourceUpdateInput,
    ) -> MutationResponseType[CapacityAndResourceType]:
        instance = await CapacityAndResource.objects.aget(id=id)
        return await ModelMutation(CapacityAndResourceSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def bulk_update_external_dashboards(
        self,
        info: Info,
        data: list[ExternalDashboardOrderInput],
    ) -> MutationResponseType[list[ExternalDashboardType]]:
        order_by_id = {str(item.id): item.order for item in data}
        errors, dashboards = await _bulk_update_external_dashboard_order(order_by_id)
        if errors:
            return MutationResponseType(ok=False, errors=errors)
        return MutationResponseType(result=dashboards)  # type: ignore[reportAttributeAccessIssue]

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
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

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveMutation])
    async def remove_dashboard_from_home(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[ExternalDashboardType]:
        instance = await ExternalDashboard.objects.aget(id=id)
        instance.show_on_home = False
        await instance.asave(update_fields=["show_on_home"])
        return MutationResponseType(result=instance)  # type: ignore[reportAttributeAccessIssue]

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveDelete], handle_django_errors=False)
    async def delete_external_dashboard(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> DeleteMutationResponseType:
        return await handle_delete_mutation(ExternalDashboard, id=id)

    @strawberry_django.mutation(permission_classes=[IsStaffOrAboveDelete], handle_django_errors=False)
    async def delete_capacity_and_resource(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> DeleteMutationResponseType:
        return await handle_delete_mutation(CapacityAndResource, id=id)
