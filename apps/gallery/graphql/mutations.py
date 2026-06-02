import strawberry
import strawberry_django

from apps.gallery.models import GalleryAlbum, GalleryImage
from apps.gallery.serializers import (
    GalleryAlbumSerializer,
    GalleryAlbumUpdateSerializer,
    GalleryImageSerializer,
)
from main.graphql.context import Info
from main.graphql.permissions import IsAuthenticated
from utils.graphql.mutations import ModelMutation
from utils.graphql.types import MutationResponseType

from .inputs import GalleryAlbumCreateInput, GalleryAlbumUpdateInput, GalleryImageCreateInput
from .types import GalleryAlbumType, GalleryImageType


@strawberry.type
class Mutation:
    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def create_gallery_album(
        self,
        info: Info,
        data: GalleryAlbumCreateInput,
    ) -> MutationResponseType[GalleryAlbumType]:
        return await ModelMutation(GalleryAlbumSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def update_gallery_album(
        self,
        info: Info,
        id: strawberry.ID,
        data: GalleryAlbumUpdateInput,
    ) -> MutationResponseType[GalleryAlbumType]:
        instance = await GalleryAlbum.objects.aget(id=id)
        return await ModelMutation(GalleryAlbumUpdateSerializer).handle_update_mutation(data, info, instance)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def create_gallery_image(
        self,
        info: Info,
        data: GalleryImageCreateInput,
    ) -> MutationResponseType[GalleryImageType]:
        return await ModelMutation(GalleryImageSerializer).handle_create_mutation(data, info)

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def delete_gallery_image(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[GalleryImageType]:
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _delete() -> MutationResponseType:
            try:
                obj = GalleryImage.objects.get(id=id)
                obj.delete()
                return MutationResponseType(ok=True)
            except GalleryImage.DoesNotExist:
                return MutationResponseType(ok=False)

        return await _delete()

    @strawberry_django.mutation(permission_classes=[IsAuthenticated])
    async def delete_gallery_album(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> MutationResponseType[GalleryAlbumType]:
        instance = await GalleryAlbum.objects.aget(id=id)
        await instance.adelete()
        return MutationResponseType(ok=True)
