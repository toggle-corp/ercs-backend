import typing

from django.core.exceptions import ValidationError
from django.db import models
from django_choices_field import IntegerChoicesField
from django_stubs_ext.db.models.manager import RelatedManager

from apps.common.models import BaseModel


class ReportContentType(models.IntegerChoices):
    FILE = 10, "File"
    IFRAME = 20, "IFrame"


class ReportVisibility(models.IntegerChoices):
    PUBLIC = 10, "Public"
    PRIVATE = 20, "Private"


class ThematicArea(BaseModel):
    """Controlled vocabulary for report thematic areas."""

    name = models.CharField[str, str](max_length=255, unique=True)

    class Meta:
        verbose_name = "Thematic Area"
        verbose_name_plural = "Thematic Areas"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Report(BaseModel):
    """Unified model for file-upload and iframe-embed reports.

    Visibility rules:
    - PUBLIC → PRIVATE is allowed (redact a report).
    - PRIVATE → PUBLIC is blocked at save() and must also be enforced at the API level.

    Content-type rules:
    - FILE: `file` field must be populated; `iframe_url` must be empty.
    - IFRAME: `iframe_url` must be populated; `file` must be empty.
    """

    ContentType = ReportContentType  # convenience alias
    Visibility = ReportVisibility  # convenience alias

    title = models.CharField[str, str](max_length=500)
    description = models.TextField[str | None, str | None](null=True, blank=True)
    cover_image = models.ImageField(upload_to="reports/covers/", null=True, blank=True)
    content_type: int = IntegerChoicesField(choices_enum=ReportContentType)
    file = models.FileField(upload_to="reports/", null=True, blank=True)
    iframe_url = models.URLField[str | None, str | None](null=True, blank=True)
    visibility: int = IntegerChoicesField(choices_enum=ReportVisibility, default=ReportVisibility.PUBLIC)
    thematic_area = models.ForeignKey(
        ThematicArea,
        on_delete=models.PROTECT,
        related_name="reports",
    )
    region = models.ForeignKey(
        "geo.AdminArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reports",
    )
    disaster_type = models.CharField[str | None, str | None](max_length=255, null=True, blank=True)
    owner = models.CharField[str | None, str | None](max_length=255, null=True, blank=True)
    uploaded_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="uploaded_reports",
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # reverse relation type hints
    newspost_reports: typing.ClassVar[RelatedManager["apps.content.models.NewsPostReport"]]  # type: ignore[name-defined]

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        if self.content_type == ReportContentType.FILE and not self.file:
            raise ValidationError({"file": "A file is required when content_type is FILE."})
        if self.content_type == ReportContentType.IFRAME and not self.iframe_url:
            raise ValidationError({"iframe_url": "An iframe URL is required when content_type is IFRAME."})

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            try:
                previous = Report.objects.get(pk=self.pk)
                if previous.visibility == ReportVisibility.PRIVATE and self.visibility == ReportVisibility.PUBLIC:
                    raise ValidationError(
                        "Cannot change visibility from PRIVATE to PUBLIC.",
                    )
            except Report.DoesNotExist:
                pass
        super().save(*args, **kwargs)
