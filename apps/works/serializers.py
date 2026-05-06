import typing

from rest_framework import serializers

from apps.common.models import ContentType

from .models import EmergencyAlert, EmergencyAlertIframeUrl


class EmergencyAlertIframeUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyAlertIframeUrl
        fields = ["id", "url"]


class EmergencyAlertSerializer(serializers.ModelSerializer):
    iframe_urls = EmergencyAlertIframeUrlSerializer(many=True, required=False)

    class Meta:
        model = EmergencyAlert
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

        if content_type == ContentType.FILE and not file:
            raise serializers.ValidationError({"file": "A file is required when content_type is FILE."})
        if content_type == ContentType.IFRAME and not iframe_urls:
            raise serializers.ValidationError(
                {"iframe_urls": "At least one iframe URL is required when content_type is IFRAME."},
            )
        return attrs

    def _sync_iframe_urls(self, alert: EmergencyAlert, iframe_urls_data: list) -> None:
        alert.iframe_urls.all().delete()
        EmergencyAlertIframeUrl.objects.bulk_create(
            [EmergencyAlertIframeUrl(alert=alert, **iframe_url) for iframe_url in iframe_urls_data],
        )

    @typing.override
    def create(self, validated_data: dict) -> EmergencyAlert:
        request = self.context.get("request")
        iframe_urls_data = validated_data.pop("iframe_urls", [])
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data.setdefault("uploaded_by", request.user)
        alert = super().create(validated_data)
        if iframe_urls_data:
            self._sync_iframe_urls(alert, iframe_urls_data)
        return alert

    @typing.override
    def update(self, instance: EmergencyAlert, validated_data: dict) -> EmergencyAlert:
        iframe_urls_data = validated_data.pop("iframe_urls", None)
        alert = super().update(instance, validated_data)
        if iframe_urls_data is not None:
            self._sync_iframe_urls(alert, iframe_urls_data)
        return alert
