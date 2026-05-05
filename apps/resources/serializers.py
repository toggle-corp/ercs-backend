import typing

from rest_framework import serializers

from .models import Resource, ResourceContentType, ResourceIframeUrl


class ResourceIframeUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceIframeUrl
        fields = ["id", "url"]


class ResourceSerializer(serializers.ModelSerializer):
    iframe_urls = ResourceIframeUrlSerializer(many=True, required=False)

    class Meta:
        model = Resource
        fields = [
            "title",
            "description",
            "content_type",
            "file",
            "iframe_urls",
            "is_published",
            "published_at",
            "uploaded_by",
            "region",
        ]
        extra_kwargs = {
            "uploaded_by": {"required": False},
            "published_at": {"read_only": True},
        }

    @typing.override
    def validate(self, attrs: dict) -> dict:
        content_type = attrs.get("content_type", getattr(self.instance, "content_type", None))
        file = attrs.get("file", getattr(self.instance, "file", None))
        iframe_urls = attrs.get("iframe_urls", [])

        if content_type == ResourceContentType.FILE and not file:
            raise serializers.ValidationError({"file": "A file is required when content_type is FILE."})
        if content_type == ResourceContentType.IFRAME and not iframe_urls:
            raise serializers.ValidationError({"iframe_urls": "At least one iframe URL is required when content_type is IFRAME."})
        return attrs

    @typing.override
    def create(self, validated_data: dict) -> Resource:
        request = self.context.get("request")
        iframe_urls_data = validated_data.pop("iframe_urls", [])
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data.setdefault("uploaded_by", request.user)
        resource = super().create(validated_data)
        for iframe_url in iframe_urls_data:
            ResourceIframeUrl.objects.create(resource=resource, **iframe_url)
        return resource

    @typing.override
    def update(self, instance: Resource, validated_data: dict) -> Resource:
        iframe_urls_data = validated_data.pop("iframe_urls", None)
        resource = super().update(instance, validated_data)
        if iframe_urls_data is not None:
            resource.iframe_urls.all().delete()
            for iframe_url in iframe_urls_data:
                ResourceIframeUrl.objects.create(resource=resource, **iframe_url)
        return resource