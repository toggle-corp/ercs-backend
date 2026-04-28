import typing

import strawberry
import strawberry_django

from apps.gallery.models import GalleryAlbum, GalleryImage


@strawberry_django.filters.filter(GalleryAlbum, lookups=True)
class GalleryAlbumFilter:
    id: strawberry.ID | None = strawberry.UNSET
    created_by_id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, queryset: typing.Any, value: str, prefix: str) -> typing.Any:
        return queryset.filter(title__icontains=value)


@strawberry_django.filters.filter(GalleryImage, lookups=True)
class GalleryImageFilter:
    id: strawberry.ID | None = strawberry.UNSET
    album_id: strawberry.ID | None = strawberry.UNSET
