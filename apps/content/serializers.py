from rest_framework import serializers

from apps.reports.models import Report, ReportVisibility

from .models import NewsPost, NewsPostReport


class NewsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = [
            "title",
            "description",
            "cover_image",
            "content",
            "author",
            "region",
            "is_published",
        ]
        extra_kwargs = {
            "author": {"required": False},
        }

    def create(self, validated_data: dict) -> NewsPost:
        request = self.context.get("request")
        if request and hasattr(request, "user") and request.user.is_authenticated:
            validated_data.setdefault("author", request.user)
        return super().create(validated_data)


class NewsPostReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPostReport
        fields = ["newspost", "report", "order"]

    def validate_report(self, report: Report) -> Report:
        if report.visibility != ReportVisibility.PUBLIC:
            raise serializers.ValidationError(
                "Only PUBLIC reports can be linked to a news post.",
            )
        return report
