import typing

from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.users.factories import UserFactory

from .models import GalleryAlbum, GalleryImage


class GalleryAlbumFactory(DjangoModelFactory):
    title = Sequence(lambda n: f"Album {n}")
    created_by = SubFactory(UserFactory)

    class Meta:
        model = GalleryAlbum


class GalleryImageFactory(DjangoModelFactory):
    album = SubFactory(GalleryAlbumFactory)
    order = Sequence(lambda n: n)

    class Meta:
        model = GalleryImage


if typing.TYPE_CHECKING:
    GalleryAlbumFactory: type[DjangoModelFactory[GalleryAlbum]]
    GalleryImageFactory: type[DjangoModelFactory[GalleryImage]]
