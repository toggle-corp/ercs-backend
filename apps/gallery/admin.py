from django.contrib import admin

from .models import GalleryAlbum, GalleryImage


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 0
    fields = ["image", "caption", "order"]
    ordering = ["order"]
    readonly_fields = ["uploaded_at"]


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ["title", "cover_image", "created_by", "created_at"]
    search_fields = ["title", "description"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [GalleryImageInline]
    ordering = ["-created_at"]


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ["album", "caption", "order", "uploaded_at"]
    list_filter = ["album"]
    search_fields = ["caption"]
    readonly_fields = ["uploaded_at"]
    ordering = ["album", "order"]
