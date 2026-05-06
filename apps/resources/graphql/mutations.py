import strawberry
import strawberry_django

from apps.resources.models import Resource
from apps.resources.serializers import ResourceSerializer
from main.graphql.context import Info
from main.graphql.permissions import IsAuthenticated
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType

from .inputs import ResourceCreateInput, ResourceUpdateInput
from .types import ResourceType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def create_resource(
        self,
        info: Info,
        data: ResourceCreateInput,
    ) -> MutationResponseType[ResourceType]:
        return await ModelMutation(ResourceSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def update_resource(
        self,
        info: Info,
        id: strawberry.ID,
        data: ResourceUpdateInput,
    ) -> MutationResponseType[ResourceType]:
        instance = await Resource.objects.aget(id=id)
        return await ModelMutation(ResourceSerializer).handle_update_mutation(data, info, instance)
