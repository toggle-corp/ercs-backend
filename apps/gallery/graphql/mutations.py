import strawberry
import strawberry_django

from apps.gallery.models import GalleryAlbum, GalleryImage
from apps.gallery.serializers import (
    GalleryAlbumSerializer,
    GalleryAlbumUpdateSerializer,
    GalleryImageSerializer,
)
from main.graphql.context import Info
from main.graphql.permissions import IsAuthenticatedDelete, IsAuthenticatedMutation
from utils.graphql.mutations import ModelMutation, handle_delete_mutation
from utils.graphql.types import DeleteMutationResponseType, MutationResponseType

from .inputs import GalleryAlbumCreateInput, GalleryAlbumUpdateInput, GalleryImageCreateInput
from .types import GalleryAlbumType, GalleryImageType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsAuthenticatedMutation])
    async def create_gallery_album(
        self,
        info: Info,
        data: GalleryAlbumCreateInput,
    ) -> MutationResponseType[GalleryAlbumType]:
        return await ModelMutation(GalleryAlbumSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticatedMutation])
    async def update_gallery_album(
        self,
        info: Info,
        id: strawberry.ID,
        data: GalleryAlbumUpdateInput,
    ) -> MutationResponseType[GalleryAlbumType]:
        instance = await GalleryAlbum.objects.aget(id=id)
        return await ModelMutation(GalleryAlbumUpdateSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsAuthenticatedMutation])
    async def create_gallery_image(
        self,
        info: Info,
        data: GalleryImageCreateInput,
    ) -> MutationResponseType[GalleryImageType]:
        return await ModelMutation(GalleryImageSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticatedDelete], handle_django_errors=False)
    async def delete_gallery_image(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> DeleteMutationResponseType:
        return await handle_delete_mutation(GalleryImage, id=id)

    @strawberry_django.mutation(permission_classes=[IsAuthenticatedDelete], handle_django_errors=False)
    async def delete_gallery_album(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> DeleteMutationResponseType:
        return await handle_delete_mutation(GalleryAlbum, id=id)
