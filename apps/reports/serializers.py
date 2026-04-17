from rest_framework import serializers

from .models import Report, ReportContentType, ReportVisibility, ThematicArea


class ThematicAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThematicArea
        fields = ["name"]


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "title",
            "description",
            "content_type",
            "file",
            "iframe_url",
            "visibility",
            "thematic_area",
            "region",
            "disaster_type",
            "owner",
            "uploaded_by",
            "published_at",
        ]
        extra_kwargs = {
            "uploaded_by": {"required": False},
        }

    def validate_visibility(self, value: int) -> int:
        if self.instance and self.instance.visibility == ReportVisibility.PRIVATE and value == ReportVisibility.PUBLIC:
            raise serializers.ValidationError("Cannot change visibility from PRIVATE to PUBLIC.")
        return value

    def validate(self, data: dict) -> dict:
        content_type = data.get("content_type", getattr(self.instance, "content_type", None))
        file = data.get("file", getattr(self.instance, "file", None))
        iframe_url = data.get("iframe_url", getattr(self.instance, "iframe_url", None))

        if content_type == ReportContentType.FILE and not file:
            raise serializers.ValidationError({"file": "A file is required when content_type is FILE."})
        if content_type == ReportContentType.IFRAME and not iframe_url:
            raise serializers.ValidationError({"iframe_url": "An iframe URL is required when content_type is IFRAME."})
        return data

    def create(self, validated_data: dict) -> Report:
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data.setdefault("uploaded_by", request.user)
        return super().create(validated_data)
