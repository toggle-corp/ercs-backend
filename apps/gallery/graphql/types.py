import strawberry
import strawberry_django

from apps.gallery.models import GalleryAlbum, GalleryImage
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
    created_by_id: strawberry.ID
    created_at: strawberry.auto
    updated_at: strawberry.auto
    images: list[GalleryImageType]
