import typing

from django.db import models
from django_choices_field import IntegerChoicesField

from apps.common.models import BaseModel


class KoboForm(models.IntegerChoices):
    """The ERCS EOC Kobo forms we mirror into the local store.

    Values are stable — do not renumber. The ``asset_uid`` for each form is
    configured in ``apps.kobo.sync.FORM_SPECS`` (kept out of the DB so a form
    can be re-pointed without a migration).
    """

    EMERGENCY_ALERT = 10, "Emergency Alert"
    RAPID_NEEDS_ASSESSMENT = 20, "Rapid Needs Assessment"
    EMERGENCY_FIELD = 30, "Emergency Field"


# Kobo's `_validation_status.uid` value for a curated/approved submission.
VALIDATION_STATUS_APPROVED = "validation_status_approved"


class KoboSubmission(BaseModel):
    """A single Kobo submission, mirrored verbatim.

    The full record is preserved in ``raw``; a handful of keys are promoted to
    columns for indexing/joining/aggregation. Populated exclusively by the sync
    job (``sync_kobo``), which reconciles the table to match Kobo on every run
    """

    form: int = IntegerChoicesField(choices_enum=KoboForm)  # type: ignore[reportAssignmentType]
    asset_uid = models.CharField[str, str](max_length=32)
    kobo_id = models.IntegerField[int, int](help_text="Kobo `_id` — stable submission id, used as the upsert key.")
    submission_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Kobo `_submission_time`. Nullable: a record with a missing/unparseable value is still mirrored.",
    )
    validation_status = models.CharField[str, str](
        max_length=64,
        blank=True,
        default="",
        help_text="Kobo `_validation_status.uid`, e.g. 'validation_status_approved'. Empty if unset.",
    )
    emergency_code = models.CharField[str | None, str | None](
        max_length=128,
        null=True,
        blank=True,
        help_text="Links Alert/RNA/Field submissions for the same emergency. Derived on sync.",
    )
    region = models.ForeignKey(
        "geo.AdminArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="kobo_submissions",
        help_text="Best-effort match of the reporting region name during sync.",
    )
    raw = models.JSONField[dict, dict](help_text="The full Kobo record, verbatim.")

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Kobo Submission"
        verbose_name_plural = "Kobo Submissions"
        ordering = ["-submission_time", "-kobo_id"]
        constraints = [
            models.UniqueConstraint(fields=["asset_uid", "kobo_id"], name="uniq_kobo_submission"),
        ]
        indexes = [
            models.Index(fields=["form", "validation_status"]),
            models.Index(fields=["emergency_code"]),
        ]

    @typing.override
    def __str__(self) -> str:
        return f"{self.get_form_display()} #{self.kobo_id}"  # type: ignore[reportAttributeAccessIssue]


class KoboSyncState(BaseModel):
    """Per-form bookkeeping for the sync job.

    Exactly one row per form. Records when each form was last successfully
    fetched and how many rows it holds — this is the source of the
    ``lastFetchedAt`` surfaced to the dashboard.
    """

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILURE = "failure", "Failure"

    form: int = IntegerChoicesField(choices_enum=KoboForm, unique=True)  # type: ignore[reportAssignmentType]
    asset_uid = models.CharField[str, str](max_length=32)
    last_fetched_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last *successful* fetch+reconcile.",
    )
    last_status = models.CharField[str, str](max_length=16, choices=Status.choices, blank=True, default="")
    last_error = models.TextField[str, str](blank=True, default="")
    record_count = models.IntegerField[int, int](default=0, help_text="Rows stored for this form after the last success.")

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        verbose_name = "Kobo Sync State"
        verbose_name_plural = "Kobo Sync States"

    @typing.override
    def __str__(self) -> str:
        return f"{self.get_form_display()} — {self.last_status or 'never run'}"  # type: ignore[reportAttributeAccessIssue]
