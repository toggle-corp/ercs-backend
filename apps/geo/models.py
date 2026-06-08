import typing

from django.core.exceptions import ValidationError
from django.db import models
from django_choices_field import IntegerChoicesField
from django_stubs_ext.db.models.manager import RelatedManager

from apps.common.models import BaseModel


class AdminAreaLevel(models.IntegerChoices):
    """Hierarchy levels for administrative areas."""

    COUNTRY = 10, "Country"
    REGION = 20, "Region"
    ZONE = 30, "Zone"
    WOREDA = 40, "Woreda"


class AdminArea(BaseModel):
    """Central geo-reference model with a self-referential level hierarchy.

    Hierarchy: COUNTRY → REGION → ZONE → WOREDA.
    Seeded via import script; no admin mutations expected.
    """

    Level = AdminAreaLevel  # convenience alias

    _LEVEL_ORDER = [
        AdminAreaLevel.COUNTRY,
        AdminAreaLevel.REGION,
        AdminAreaLevel.ZONE,
        AdminAreaLevel.WOREDA,
    ]

    name = models.CharField[str, str](max_length=255)
    name_am = models.CharField[str | None, str | None](max_length=255, null=True, blank=True)
    level: int = IntegerChoicesField(choices_enum=AdminAreaLevel)  # type: ignore[reportAssignmentType]
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )
    geo_shape = models.JSONField[dict | None, dict | None](null=True, blank=True)
    pcode = models.CharField[str | None, str | None](max_length=50, unique=True, null=True, blank=True)
    ifrc_id = models.IntegerField[int | None, int | None](unique=True, null=True, blank=True, db_index=True)
    centroid_lat = models.FloatField[float | None, float | None](null=True, blank=True)
    centroid_lon = models.FloatField[float | None, float | None](null=True, blank=True)

    # reverse relation type hints
    children: typing.ClassVar[RelatedManager["AdminArea"]]

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Admin Area"
        verbose_name_plural = "Admin Areas"
        ordering = ["level", "name"]

    @typing.override
    def __str__(self) -> str:
        return f"{self.name} ({self.get_level_display()})"  # type: ignore[reportAttributeAccessIssue]

    @typing.override
    def clean(self) -> None:
        order = self._LEVEL_ORDER
        if self.parent_id is None:  # type: ignore[reportAttributeAccessIssue]
            if self.level != AdminAreaLevel.COUNTRY:
                raise ValidationError(
                    "Only COUNTRY-level areas may have no parent.",
                )
            return

        parent = AdminArea.objects.get(pk=self.parent_id)  # type: ignore[reportAttributeAccessIssue]
        try:
            parent_idx = order.index(parent.level)  # type: ignore[reportArgumentType]
            child_idx = order.index(self.level)  # type: ignore[reportArgumentType]
        except ValueError:
            raise ValidationError("Invalid level value.") from None

        if child_idx != parent_idx + 1:
            raise ValidationError(
                f"A {self.get_level_display()} must have a "  # type: ignore[reportAttributeAccessIssue]
                f"{AdminAreaLevel(order[child_idx - 1]).label if child_idx > 0 else 'Country'} "
                f"as its parent, but got a {parent.get_level_display()}.",  # type: ignore[reportAttributeAccessIssue]
            )
