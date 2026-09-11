import typing

from apps.gallery.factories import GalleryAlbumFactory, GalleryImageFactory
from apps.gallery.models import GalleryAlbum, GalleryImage
from apps.users.factories import UserFactory
from apps.users.models import User
from main.tests import TestCase


class TestGalleryMutations(TestCase):
    class Mutation:
        DELETE_GALLERY_ALBUM = """
            mutation DeleteGalleryAlbum($id: ID!) {
                deleteGalleryAlbum(id: $id) {
                    ok
                    errors
                }
            }
        """

        DELETE_GALLERY_IMAGE = """
            mutation DeleteGalleryImage($id: ID!) {
                deleteGalleryImage(id: $id) {
                    ok
                    errors
                }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff = UserFactory.create(role=User.Role.STAFF)

    def test_delete_gallery_image(self):
        self.force_login(self.staff)
        image = GalleryImageFactory.create()
        content = self.query_check(
            self.Mutation.DELETE_GALLERY_IMAGE,
            variables={"id": str(image.pk)},
        )
        resp = content["data"]["deleteGalleryImage"]
        assert resp["ok"] is True, resp
        assert not GalleryImage.objects.filter(pk=image.pk).exists()

    def test_delete_gallery_album_cascades_to_images(self):
        self.force_login(self.staff)
        album = GalleryAlbumFactory.create()
        GalleryImageFactory.create_batch(2, album=album)
        content = self.query_check(
            self.Mutation.DELETE_GALLERY_ALBUM,
            variables={"id": str(album.pk)},
        )
        resp = content["data"]["deleteGalleryAlbum"]
        assert resp["ok"] is True, resp
        assert not GalleryAlbum.objects.filter(pk=album.pk).exists()
        assert not GalleryImage.objects.filter(album_id=album.pk).exists()

    def test_unauthenticated_cannot_delete_gallery_album(self):
        self.logout()
        album = GalleryAlbumFactory.create()
        content = self.query_check(
            self.Mutation.DELETE_GALLERY_ALBUM,
            variables={"id": str(album.pk)},
        )
        self.assert_permission_denied(content, "deleteGalleryAlbum")
        assert GalleryAlbum.objects.filter(pk=album.pk).exists()

    def test_deleting_missing_gallery_album_is_reported_on_the_payload(self):
        self.force_login(self.staff)
        album = GalleryAlbumFactory.create()
        album_id = str(album.pk)
        album.delete()
        content = self.query_check(
            self.Mutation.DELETE_GALLERY_ALBUM,
            variables={"id": album_id},
        )
        resp = content["data"]["deleteGalleryAlbum"]
        assert resp["ok"] is False, resp
        assert resp["errors"][0]["messages"] == "This Gallery Album no longer exists. It may already have been deleted."
