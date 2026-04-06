import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from main.graphql.permissions import IsAuthenticated

from .filters import GalleryAlbumFilter
from .orders import GalleryAlbumOrder
from .types import GalleryAlbumType


@strawberry.type
class Query:
    gallery_albums: OffsetPaginated[GalleryAlbumType] = strawberry_django.offset_paginated(
        filters=GalleryAlbumFilter,
        order=GalleryAlbumOrder,
        permission_classes=[IsAuthenticated],
    )

    gallery_album: GalleryAlbumType = strawberry_django.field(
        permission_classes=[IsAuthenticated],
    )
