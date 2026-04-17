import typing

from django.db import models
from django.utils import timezone
from django_stubs_ext.db.models.manager import RelatedManager

from apps.common.models import BaseModel


class NewsPost(BaseModel):
    """Editorial blog/news posts. Always public — no visibility field.

    published_at is auto-set the first time is_published is flipped to True.
    Reports are linked via the ordered NewsPostReport through-table.
    """

    title = models.CharField[str, str](max_length=500)
    description = models.TextField[str | None, str | None](null=True, blank=True)
    cover_image = models.ImageField(upload_to="news/covers/", null=True, blank=True)
    content = models.TextField[str, str]()
    author = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="news_posts",
    )
    region = models.ForeignKey(
        "geo.AdminArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="news_posts",
    )
    is_published = models.BooleanField[bool, bool](default=False)
    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    reports = models.ManyToManyField(
        "reports.Report",
        through="NewsPostReport",
        related_name="news_posts",
        blank=True,
    )

    # reverse relation type hints
    newspost_reports: typing.ClassVar[RelatedManager["NewsPostReport"]]

    class Meta:
        verbose_name = "News Post"
        verbose_name_plural = "News Posts"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class NewsPostReport(models.Model):
    """Ordered join table linking NewsPost to Report.

    Constraint: report.visibility must be PUBLIC.
    Enforced in the serializer/mutation layer, not at the DB level.
    """

    newspost = models.ForeignKey(
        NewsPost,
        on_delete=models.CASCADE,
        related_name="newspost_reports",
    )
    report = models.ForeignKey(
        "reports.Report",
        on_delete=models.CASCADE,
        related_name="newspost_reports",
    )
    order = models.PositiveIntegerField[int, int](default=0)

    class Meta:
        verbose_name = "News Post Report"
        verbose_name_plural = "News Post Reports"
        ordering = ["order"]
        constraints = [
            models.UniqueConstraint(
                fields=["newspost", "report"],
                name="unique_newspost_report",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.newspost} — {self.report} (order: {self.order})"
