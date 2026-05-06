import typing

from django.core.exceptions import ValidationError
from django.db import models
from django_choices_field import IntegerChoicesField
from django_stubs_ext.db.models.manager import RelatedManager

from apps.common.models import BaseModel, ContentType


class EmergencyAlertIframeUrl(BaseModel):
    """Stores multiple iframe URLs for an emergency alert."""

    alert = models.ForeignKey(
        "EmergencyAlert",
        on_delete=models.CASCADE,
        related_name="iframe_urls",
    )
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta(BaseModel.Meta):
        verbose_name = "EmergencyAlert Iframe URL"
        verbose_name_plural = "EmergencyAlert Iframe URLs"
        ordering = ["order"]

    @typing.override
    def __str__(self) -> str:
        return self.url


class EmergencyAlert(BaseModel):
    """Unified model for file-upload and iframe-embed Emergency Alert.

    Content-type rules:
    - FILE: `file` field must be populated; `iframe_urls` must be empty.
    - IFRAME: at least one `iframe_urls` must be populated; `file` must be empty.
    """

    title = models.CharField[str, str](max_length=500)
    description = models.TextField[str | None, str | None](null=True, blank=True)
    content_type = IntegerChoicesField(choices_enum=ContentType)  # type: ignore[call-arg]
    file = models.FileField(upload_to="emergency_alerts/", null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    uploaded_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="uploaded_emergency_alerts",
    )
    region = models.ForeignKey(
        "geo.AdminArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="emergency_alerts",
    )

    iframe_urls: typing.ClassVar[RelatedManager["EmergencyAlertIframeUrl"]]

    class Meta(BaseModel.Meta):
        verbose_name = "Emergency Alert"
        verbose_name_plural = "Emergency Alerts"
        ordering = ["-created_at"]

    @typing.override
    def __str__(self) -> str:
        return self.title

    @typing.override
    def clean(self) -> None:
        if self.content_type == ContentType.FILE and not self.file:
            raise ValidationError({"file": "A file is required when content_type is FILE."})

    @typing.override
    def save(self, *args, **kwargs) -> None:
        from django.utils import timezone

        if self.pk:
            try:
                previous = EmergencyAlert.objects.get(pk=self.pk)
                if not previous.is_published and self.is_published and not self.published_at:
                    self.published_at = timezone.now()
            except EmergencyAlert.DoesNotExist:
                pass
        elif self.is_published and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)
