from django.contrib import admin

from .models import EmergencyAlert, EmergencyAlertIframeUrl


class EmergencyAlertIframeUrlInline(admin.TabularInline):
    model = EmergencyAlertIframeUrl
    extra = 1
    fields = ["url", "order"]
    ordering = ["order"]


@admin.register(EmergencyAlert)
class EmergencyAlertAdmin(admin.ModelAdmin):
    inlines = [EmergencyAlertIframeUrlInline]
    list_display = [
        "title",
        "content_type",
        "is_published",
        "region",
        "uploaded_by",
        "published_at",
        "created_at",
    ]
    list_filter = ["content_type", "is_published", "region"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at", "published_at"]
    ordering = ["-created_at"]
