from django.contrib import admin

from .models import CapacityAndResource, CapacityAndResourceIframeUrl, ExternalDashboard


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


class CapacityAndResourceIframeUrlInline(admin.TabularInline):
    model = CapacityAndResourceIframeUrl
    extra = 1
    autocomplete_fields = ["dashboard"]


@admin.register(CapacityAndResource)
class CapacityAndResourceAdmin(admin.ModelAdmin):
    inlines = [CapacityAndResourceIframeUrlInline]
    list_display = [
        "title",
        "region",
        "order",
        "is_active",
        "created_by",
        "created_at",
    ]
    list_filter = ["is_active", "region"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["order"]
