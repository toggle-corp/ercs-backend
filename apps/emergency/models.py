import typing
import uuid

from django.db import models


# TODO: This needs to be better defined later.
class Emergency(models.Model):
    """Emergency events synced from the IFRC GO API.

    Read-only within the application. Populated exclusively by the sync job.
    go_id is the GO platform's native integer ID and is used as the upsert key.
    synced_at is updated on every sync write (auto_now=True).
    """

    id = models.UUIDField[uuid.UUID, uuid.UUID](
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    go_id = models.IntegerField[int, int](unique=True)
    name = models.CharField[str, str](max_length=500)
    disaster_type = models.CharField[str, str](max_length=255)
    status = models.CharField[str, str](max_length=100)
    region = models.ForeignKey(
        "geo.AdminArea",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="emergencies",
        help_text="Matched by name/pcode during sync.",
    )
    start_date = models.DateField()
    affected_pop = models.IntegerField[int | None, int | None](null=True, blank=True)
    go_url = models.URLField[str | None, str | None](null=True, blank=True)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Emergency"
        verbose_name_plural = "Emergencies"
        ordering = ["-start_date"]

    @typing.override
    def __str__(self) -> str:
        return f"{self.name} ({self.disaster_type})"
