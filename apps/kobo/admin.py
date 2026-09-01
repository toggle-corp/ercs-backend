"""Read-only admin for the Kobo mirror.

Both models are owned entirely by the sync job: ``KoboSubmission`` rows are
re-upserted from Kobo on every run and pruned when Kobo drops them, and
``KoboSyncState`` is rewritten each run. An edit made here would be silently
reverted the next night, so the admin exposes the data for inspection only.
"""

import typing

from django.contrib import admin
from django.http import HttpRequest

from apps.kobo.models import KoboSubmission, KoboSyncState


class ReadOnlyAdmin(admin.ModelAdmin):  # type: ignore[reportMissingTypeArgument]
    """Inspect-only: Django renders the detail view read-only without change perms."""

    @typing.override
    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    @typing.override
    def has_change_permission(self, request: HttpRequest, obj: object = None) -> bool:
        return False

    @typing.override
    def has_delete_permission(self, request: HttpRequest, obj: object = None) -> bool:
        # A deleted row would simply reappear on the next sync.
        return False


@admin.register(KoboSubmission)
class KoboSubmissionAdmin(ReadOnlyAdmin):
    list_display = ("kobo_id", "form", "validation_status", "emergency_code", "submission_time")
    list_filter = ("form", "validation_status")
    search_fields = ("kobo_id", "emergency_code")
    date_hierarchy = "submission_time"
    list_select_related = ("region",)


@admin.register(KoboSyncState)
class KoboSyncStateAdmin(ReadOnlyAdmin):
    list_display = ("form", "last_status", "last_fetched_at", "record_count")
