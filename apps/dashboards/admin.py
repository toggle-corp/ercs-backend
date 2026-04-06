from django.contrib import admin

from .models import ExternalDashboard


@admin.register(ExternalDashboard)
class ExternalDashboardAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "page",
        "region",
        "order",
        "is_active",
        "show_on_home",
        "created_by",
        "created_at",
    ]
    list_filter = ["page", "is_active", "show_on_home"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["page", "order"]
