from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.users.factories import UserFactory

from .models import GalleryAlbum, GalleryImage


class GalleryAlbumFactory(DjangoModelFactory[GalleryAlbum]):
    title = Sequence(lambda n: f"Album {n}")
    created_by = SubFactory(UserFactory)

    class Meta:  # type: ignore[misc]
        model = GalleryAlbum


class GalleryImageFactory(DjangoModelFactory[GalleryImage]):
    album = SubFactory(GalleryAlbumFactory)
    order = Sequence(lambda n: n)

    class Meta:  # type: ignore[misc]
        model = GalleryImage
