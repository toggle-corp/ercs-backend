from django.contrib import admin

from apps.kobo.models import KoboSubmission, KoboSyncState


@admin.register(KoboSubmission)
class KoboSubmissionAdmin(admin.ModelAdmin):
    list_display = ("kobo_id", "form", "validation_status", "emergency_code", "region", "submission_time")
    list_filter = ("form", "validation_status")
    search_fields = ("kobo_id", "emergency_code")
    date_hierarchy = "submission_time"
    readonly_fields = ("raw",)


@admin.register(KoboSyncState)
class KoboSyncStateAdmin(admin.ModelAdmin):
    list_display = ("form", "last_status", "last_fetched_at", "record_count")
    readonly_fields = ("last_error",)
