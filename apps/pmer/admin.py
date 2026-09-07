from django.contrib import admin

from .models import PmerReport


@admin.register(PmerReport)
class PmerReportAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "report_type", "visibility"]
    list_filter = ["category", "report_type", "visibility"]
    search_fields = ["title"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
