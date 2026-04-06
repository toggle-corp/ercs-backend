import strawberry
import strawberry_django

from apps.gallery.models import GalleryAlbum, GalleryImage


@strawberry_django.order_type(GalleryAlbum)
class GalleryAlbumOrder:
    title: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.order_type(GalleryImage)
class GalleryImageOrder:
    order: strawberry.auto
    uploaded_at: strawberry.auto
