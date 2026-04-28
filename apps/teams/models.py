import typing

from django.db import models
from django_choices_field import IntegerChoicesField
from django_stubs_ext.db.models.manager import RelatedManager

from apps.common.models import BaseModel


class TeamMemberSex(models.IntegerChoices):
    MALE = 10, "Male"
    FEMALE = 20, "Female"
    OTHER = 30, "Other"


class Team(BaseModel):
    """Auth-gated response team registry. Login required to access."""

    name = models.CharField[str, str](max_length=255)
    description = models.TextField[str | None, str | None](null=True, blank=True)

    # reverse relation type hints
    members: typing.ClassVar[RelatedManager["TeamMember"]]

    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TeamMember(BaseModel):
    """Individual member belonging to a Team."""

    Sex = TeamMemberSex  # convenience alias

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="members",
    )
    name = models.CharField[str, str](max_length=255)
    position = models.CharField[str, str](max_length=255)
    email = models.EmailField[str | None, str | None](null=True, blank=True)
    phone_number = models.CharField[str | None, str | None](max_length=50, null=True, blank=True)
    sex: int = IntegerChoicesField(choices_enum=TeamMemberSex, null=True, blank=True)
    region = models.ForeignKey(
        "geo.AdminArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="team_members",
        help_text="AdminArea at region level (level=20).",
    )
    woreda = models.ForeignKey(
        "geo.AdminArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="team_members_by_woreda",
        help_text="AdminArea at woreda level (level=40).",
    )
    training = models.CharField[str | None, str | None](max_length=500, null=True, blank=True)
    field_of_study = models.CharField[str | None, str | None](max_length=500, null=True, blank=True)
    order = models.PositiveIntegerField[int, int](default=0)

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return f"{self.name} — {self.position} ({self.team})"
