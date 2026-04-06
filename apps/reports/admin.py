from django.contrib import admin

from .models import Report, ThematicArea


@admin.register(ThematicArea)
class ThematicAreaAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "content_type",
        "visibility",
        "thematic_area",
        "region",
        "disaster_type",
        "uploaded_by",
        "published_at",
        "created_at",
    ]
    list_filter = ["content_type", "visibility", "thematic_area", "disaster_type"]
    search_fields = ["title", "description", "owner"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
