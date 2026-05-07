import strawberry
import strawberry_django
from django.db.models import Q

from apps.gallery.models import GalleryAlbum, GalleryImage


@strawberry_django.filters.filter(GalleryAlbum, lookups=True)
class GalleryAlbumFilter:
    id: strawberry.ID | None = strawberry.UNSET
    created_by_id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)


@strawberry_django.filters.filter(GalleryImage, lookups=True)
class GalleryImageFilter:
    id: strawberry.ID | None = strawberry.UNSET
    album_id: strawberry.ID | None = strawberry.UNSET
