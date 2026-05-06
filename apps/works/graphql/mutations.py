import strawberry
import strawberry_django

from apps.works.models import EmergencyAlert
from apps.works.serializers import EmergencyAlertSerializer
from main.graphql.context import Info
from main.graphql.permissions import IsAuthenticated
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType

from .inputs import EmergencyAlertCreateInput, EmergencyAlertUpdateInput
from .types import EmergencyAlertType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def create_emergencyAlert(
        self,
        info: Info,
        data: EmergencyAlertCreateInput,
    ) -> MutationResponseType[EmergencyAlertType]:
        return await ModelMutation(EmergencyAlertSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def update_emergencyAlert(
        self,
        info: Info,
        id: strawberry.ID,
        data: EmergencyAlertUpdateInput,
    ) -> MutationResponseType[EmergencyAlertType]:
        instance = await EmergencyAlert.objects.aget(id=id)
        return await ModelMutation(EmergencyAlertSerializer).handle_update_mutation(data, info, instance)
