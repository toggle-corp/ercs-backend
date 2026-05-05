from django.contrib import admin

from .models import Resource, ResourceIframeUrl


class ResourceIframeUrlInline(admin.TabularInline):
    model = ResourceIframeUrl
    extra = 1


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    inlines = [ResourceIframeUrlInline]
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