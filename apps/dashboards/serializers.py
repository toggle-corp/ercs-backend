import typing

from rest_framework import serializers

from .models import ExternalDashboard


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
