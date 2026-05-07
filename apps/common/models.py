import uuid

from django.db import models


class TimestampedModel(models.Model):
    """Abstract base providing created_at and updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(TimestampedModel):
    """Abstract base with UUID primary key and timestamps."""

    id = models.UUIDField[uuid.UUID, uuid.UUID](
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta(TimestampedModel.Meta):
        abstract = True
