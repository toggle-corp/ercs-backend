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
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data.setdefault("created_by", request.user)
        return super().create(validated_data)


class CapacityAndResourceIframeUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapacityAndResourceIframeUrl
        fields = ["id", "dashboard", "order"]


class CapacityAndResourceSerializer(serializers.ModelSerializer):
    iframe_urls = CapacityAndResourceIframeUrlSerializer(many=True, required=False)

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
    def create(self, validated_data: dict) -> CapacityAndResource:
        request = self.context.get("request")
        iframe_urls_data = validated_data.pop("iframe_urls", [])
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data.setdefault("created_by", request.user)
        instance = super().create(validated_data)
        for item in iframe_urls_data:
            CapacityAndResourceIframeUrl.objects.create(capacity_and_resource=instance, **item)
        return instance

    @typing.override
    def update(self, instance: CapacityAndResource, validated_data: dict) -> CapacityAndResource:
        iframe_urls_data = validated_data.pop("iframe_urls", None)
        instance = super().update(instance, validated_data)
        if iframe_urls_data is not None:
            instance.iframe_urls.all().delete()
            for item in iframe_urls_data:
                CapacityAndResourceIframeUrl.objects.create(capacity_and_resource=instance, **item)
        return instance
