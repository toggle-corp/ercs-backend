import typing

from django.contrib import admin

from .models import CapacityAndResource, ExternalDashboard


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
    list_select_related = ("created_by",)


@admin.register(CapacityAndResource)
class CapacityAndResourceAdmin(admin.ModelAdmin):
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
    list_select_related = True
    autocomplete_fields = (
        "region",
        "dashboards",
    )

    @typing.override
    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "region",
            )
            .prefetch_related(
                "dashboards",
            )
        )
