import strawberry
import strawberry_django
from asgiref.sync import sync_to_async

from apps.gallery.models import GalleryAlbum, GalleryImage
from apps.users.graphql.types import UserType
from utils.graphql.types import DjangoFileType


@strawberry_django.type(GalleryImage)
class GalleryImageType:
    id: strawberry.ID
    album_id: strawberry.ID
    image: DjangoFileType
    caption: strawberry.auto
    order: strawberry.auto
    uploaded_at: strawberry.auto


@strawberry_django.type(GalleryAlbum)
class GalleryAlbumType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    cover_image: GalleryImageType | None
    created_by: UserType
    created_at: strawberry.auto
    updated_at: strawberry.auto

    @strawberry_django.field
    async def images_count(self) -> int:
        return await sync_to_async(self.images.count)()  # type: ignore[reportAttributeAccessIssue]
