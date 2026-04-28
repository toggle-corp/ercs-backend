import typing

from django.db import models
from django_choices_field import IntegerChoicesField

from apps.common.models import BaseModel


class DashboardPage(models.IntegerChoices):
    """Site pages where an external dashboard can be embedded."""

    HOME = 10, "Home"
    OPERATIONS = 20, "Operations"
    PROJECT_MAPPING = 30, "Project Mapping"
    CAPACITY_RESOURCES = 40, "Capacity & Resources"
    ALERTS = 50, "Alerts"
    DISASTER_RESPONSE = 60, "Disaster Response"


class ExternalDashboard(BaseModel):
    """Power BI / iframe dashboards embedded across site pages via CMS."""

    Page = DashboardPage  # convenience alias

    title = models.CharField[str, str](max_length=500)
    description = models.TextField[str | None, str | None](null=True, blank=True)
    url = models.URLField[str, str]()
    page: int = IntegerChoicesField(choices_enum=DashboardPage)  # type: ignore[reportAssignmentType]
    region = models.ForeignKey(
        "geo.AdminArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="dashboards",
    )
    show_on_home = models.BooleanField[bool, bool](
        default=False,
        help_text="Surface this dashboard as a quick link on the homepage.",
    )
    order = models.PositiveIntegerField[int, int](default=0)
    is_active = models.BooleanField[bool, bool](default=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="created_dashboards",
    )

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = "External Dashboard"
        verbose_name_plural = "External Dashboards"
        ordering = ["page", "order"]

    @typing.override
    def __str__(self) -> str:
        return f"{self.title} ({self.get_page_display()})"  # type: ignore[reportAttributeAccessIssue]
