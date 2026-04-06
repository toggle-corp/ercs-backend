import strawberry
import strawberry_django

from apps.gallery.models import GalleryAlbum, GalleryImage


@strawberry_django.filters.filter(GalleryAlbum, lookups=True)
class GalleryAlbumFilter:
    id: strawberry.ID | None = strawberry.UNSET
    created_by_id: strawberry.ID | None = strawberry.UNSET


@strawberry_django.filters.filter(GalleryImage, lookups=True)
class GalleryImageFilter:
    id: strawberry.ID | None = strawberry.UNSET
    album_id: strawberry.ID | None = strawberry.UNSET
