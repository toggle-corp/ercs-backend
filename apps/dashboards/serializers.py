import typing

from rest_framework import serializers

from .models import CapacityAndResource, CapacityAndResourceIframeUrl, ExternalDashboard


class ExternalDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalDashboard
        fields = [
            "title",
            "description",
            "url",
            "page",
            "region",
            "show_on_home",
            "order",
            "is_active",
            "created_by",
        ]
        extra_kwargs = {
            "created_by": {"required": False},
        }

    @typing.override
    def create(self, validated_data: dict) -> ExternalDashboard:
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data.setdefault("created_by", request.user)
        return super().create(validated_data)


class CapacityAndResourceIframeUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacityAndResourceIframeUrl
        fields = ["id", "dashboard", "order"]


class CapacityAndResourceSerializer(serializers.ModelSerializer):
    iframe_urls = CapacityAndResourceIframeUrlSerializer(many=True, required=True)

    class Meta:
        model = CapacityAndResource
        fields = [
            "title",
            "description",
            "region",
            "is_active",
            "order",
            "iframe_urls",
            "created_by",
        ]
        extra_kwargs = {
            "created_by": {"required": False},
        }

    @typing.override
    def validate(self, attrs: dict) -> dict:
        if not self.instance:
            iframe_urls = attrs.get("iframe_urls", [])
            if not iframe_urls:
                raise serializers.ValidationError({"iframe_urls": "At least one iframe URL is required."})
        return attrs

    @typing.override
    def create(self, validated_data: dict) -> CapacityAndResource:
        request = self.context.get("request")
        iframe_urls_data = validated_data.pop("iframe_urls", [])
        if request and hasattr(request, "user"):
            validated_data.setdefault("created_by", request.user)
        instance = super().create(validated_data)
        CapacityAndResourceIframeUrl.objects.bulk_create(
            [CapacityAndResourceIframeUrl(capacity_and_resource=instance, **item) for item in iframe_urls_data],
        )
        return instance

    @typing.override
    def update(self, instance: CapacityAndResource, validated_data: dict) -> CapacityAndResource:
        iframe_urls_data = validated_data.pop("iframe_urls", None)
        instance = super().update(instance, validated_data)
        if iframe_urls_data is not None:
            instance.iframe_urls.all().delete()
            CapacityAndResourceIframeUrl.objects.bulk_create(
                [CapacityAndResourceIframeUrl(capacity_and_resource=instance, **item) for item in iframe_urls_data],
            )
        return instance
