from django.contrib import admin

from .models import NewsPost, NewsPostReport


class NewsPostReportInline(admin.TabularInline):
    model = NewsPostReport
    extra = 0
    fields = ["report", "order"]
    ordering = ["order"]


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "region", "is_published", "published_at", "created_at"]
    list_filter = ["is_published", "region"]
    search_fields = ["title", "description"]
    readonly_fields = ["published_at", "created_at", "updated_at"]
    inlines = [NewsPostReportInline]
    ordering = ["-created_at"]


@admin.register(NewsPostReport)
class NewsPostReportAdmin(admin.ModelAdmin):
    list_display = ["newspost", "report", "order"]
    ordering = ["newspost", "order"]
