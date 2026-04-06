import datetime
import typing
import uuid

from django.db import models
from django_stubs_ext.db.models.manager import RelatedManager

from apps.common.models import BaseModel


class GalleryAlbum(BaseModel):
    """Auth-gated photo album. Login required to access.

    cover_image is a nullable FK to GalleryImage, set after images are uploaded.
    The forward string reference ('GalleryImage') avoids a circular import.
    on_delete=SET_NULL so deleting the cover image does not cascade to the album.
    """

    title = models.CharField[str, str](max_length=500)
    description = models.TextField[str | None, str | None](null=True, blank=True)
    cover_image = models.ForeignKey(
        "GalleryImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cover_for_albums",
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="created_albums",
    )

    # reverse relation type hints
    images: typing.ClassVar[RelatedManager["GalleryImage"]]

    class Meta:
        verbose_name = "Gallery Album"
        verbose_name_plural = "Gallery Albums"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class GalleryImage(models.Model):
    """Individual image within a GalleryAlbum.

    Uses uploaded_at instead of the standard created_at/updated_at pair.
    on_delete=CASCADE so all images are removed when the album is deleted.
    """

    id = models.UUIDField[uuid.UUID, uuid.UUID](
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    album = models.ForeignKey(
        GalleryAlbum,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="gallery/")
    caption = models.CharField[str | None, str | None](max_length=500, null=True, blank=True)
    order = models.PositiveIntegerField[int, int](default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.album.title} — {self.caption or f'image {self.order}'}"
