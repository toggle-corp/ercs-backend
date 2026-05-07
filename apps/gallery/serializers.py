import typing

from rest_framework import serializers

from .models import GalleryAlbum, GalleryImage


class GalleryAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryAlbum
        fields = ["title", "description", "created_by"]
        extra_kwargs = {
            "created_by": {"required": False},
        }

    @typing.override
    def create(self, validated_data: dict) -> GalleryAlbum:
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data.setdefault("created_by", request.user)
        return super().create(validated_data)


class GalleryAlbumUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryAlbum
        fields = ["title", "description", "cover_image"]


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ["album", "image", "caption", "order"]
