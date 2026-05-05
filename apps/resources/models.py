import typing

from django.core.exceptions import ValidationError
from django.db import models
from django_choices_field import IntegerChoicesField

from apps.common.models import BaseModel


class ResourceContentType(models.IntegerChoices):
    """Determines how the resource content is stored and rendered."""

    FILE = 10, "File"
    IFRAME = 20, "IFrame"


class ResourceIframeUrl(BaseModel):
    """Stores multiple iframe URLs for a resource."""

    resource = models.ForeignKey(
        "Resource",
        on_delete=models.CASCADE,
        related_name="iframe_urls",
    )
    url = models.URLField()

    class Meta:
        verbose_name = "Resource Iframe URL"
        verbose_name_plural = "Resource Iframe URLs"

    @typing.override
    def __str__(self) -> str:
        return self.url


class Resource(BaseModel):
    """Unified model for file-upload and iframe-embed resources.

    Content-type rules:
    - FILE: `file` field must be populated; `iframe_urls` must be empty.
    - IFRAME: at least one `iframe_urls` must be populated; `file` must be empty.
    """

    ContentType = ResourceContentType

    title = models.CharField[str, str](max_length=500)
    description = models.TextField[str | None, str | None](null=True, blank=True)
    content_type: int = IntegerChoicesField(choices_enum=ResourceContentType) 
    file = models.FileField(upload_to="resources/", null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    uploaded_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="uploaded_resources",
    )
    region = models.ForeignKey(
        "geo.AdminArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resources",
    )

    class Meta:
        verbose_name = "Resource"
        verbose_name_plural = "Resources"
        ordering = ["-created_at"]

    @typing.override
    def __str__(self) -> str:
        return self.title

    @typing.override
    def clean(self) -> None:
        if self.content_type == ResourceContentType.FILE and not self.file:
            raise ValidationError({"file": "A file is required when content_type is FILE."})

    @typing.override
    def save(self, *args, **kwargs) -> None:
        from django.utils import timezone

        if self.pk:
            try:
                previous = Resource.objects.get(pk=self.pk)
                if not previous.is_published and self.is_published and not self.published_at:
                    self.published_at = timezone.now()
            except Resource.DoesNotExist:
                pass
        elif self.is_published and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)