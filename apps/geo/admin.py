from django.contrib import admin

from apps.common.admin import ReadOnlyMixin

from .models import AdminArea


@admin.register(AdminArea)
class AdminAreaAdmin(ReadOnlyMixin, admin.ModelAdmin):
    list_display = ["name", "name_am", "level", "parent", "pcode"]
    list_filter = ["level"]
    search_fields = ["name", "name_am", "pcode"]
    ordering = ["level", "name"]
