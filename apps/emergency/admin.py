from django.contrib import admin

from apps.common.admin import ReadOnlyMixin

from .models import Emergency


@admin.register(Emergency)
class EmergencyAdmin(ReadOnlyMixin, admin.ModelAdmin):
    list_display = [
        "name",
        "disaster_type",
        "status",
        "region",
        "start_date",
        "affected_pop",
        "synced_at",
    ]
    list_filter = ["disaster_type", "status"]
    search_fields = ["name", "go_id"]
    ordering = ["-start_date"]
