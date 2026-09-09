import typing

from django.db import models
from django_choices_field import IntegerChoicesField

from apps.common.models import BaseModel
from apps.reports.models import ReportVisibility


class PmerReportCategory(models.IntegerChoices):
    """Thematic category a PMER report belongs to."""

    DPR = 10, "DPR (Disaster Preparedness Report)"
    DRR = 20, "DRR (Disaster Risk Reduction)"
    HEALTH_AND_WASH = 30, "Health & WASH"
    VOLUNTEER_SERVICE_MEMBERSHIP = 40, "Volunteer Service / Membership"


class PmerReportDocumentType(models.IntegerChoices):
    """Kind of PMER document.

    Named `...DocumentType` rather than `PmerReportType` because the latter is
    already the GraphQL object type for `PmerReport`; reusing it would collide
    at registration (see `ReportType`/`ReportTypeEnum` in apps.reports).
    """

    STRATEGIC_PLAN = 10, "Strategic Plan"
    ANNUAL_PLAN = 20, "Annual Plan"
    ANNUAL_REPORT = 30, "Annual Report"
    MID_TERM_REVIEW_REPORT = 40, "Mid-term Review Report"


class PmerReport(BaseModel):
    """Planning, Monitoring, Evaluation and Reporting (PMER) document."""

    Category = PmerReportCategory  # convenience alias
    DocumentType = PmerReportDocumentType  # convenience alias
    Visibility = ReportVisibility  # convenience alias

    title = models.CharField[str, str](max_length=500)
    description = models.TextField[str | None, str | None](null=True, blank=True)
    file = models.FileField(upload_to="pmer/")
    category: int = IntegerChoicesField(choices_enum=PmerReportCategory)  # type: ignore[reportAssignmentType]
    report_type: int = IntegerChoicesField(choices_enum=PmerReportDocumentType)  # type: ignore[reportAssignmentType]
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="created_pmer_reports",
    )
    region = models.ForeignKey(
        "geo.AdminArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pmer_region",
    )
    department = models.CharField[str | None, str | None](max_length=250, null=True, blank=True)
    project = models.CharField[str | None, str | None](max_length=250, null=True, blank=True)
    visibility: int = IntegerChoicesField(choices_enum=ReportVisibility, default=ReportVisibility.PUBLIC)  # type: ignore[reportAssignmentType]

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = "PMER Report"
        verbose_name_plural = "PMER Reports"
        ordering = ["-created_at"]

    @typing.override
    def __str__(self) -> str:
        return self.title
