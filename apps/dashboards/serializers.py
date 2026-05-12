import typing

from rest_framework import serializers

from apps.geo.models import AdminArea

from .models import CapacityAndResource, DashboardPage, ExternalDashboard


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


class CapacityAndResourceSerializer(serializers.ModelSerializer):
    dashboards = serializers.PrimaryKeyRelatedField(
        queryset=ExternalDashboard.objects.filter(
            page=DashboardPage.CAPACITY_RESOURCES,
        ),
        many=True,
        write_only=True,
        required=True,
    )

    region = serializers.PrimaryKeyRelatedField(
        queryset=AdminArea.objects.all(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = CapacityAndResource
        fields = [
            "id",
            "title",
            "description",
            "region",
            "is_active",
            "order",
            "dashboards",
        ]

    @typing.override
    def create(self, validated_data: dict[str, typing.Any]) -> CapacityAndResource:
        request = self.context["request"]
        dashboards = validated_data.pop("dashboards")
        capacity_resource = CapacityAndResource.objects.create(
            created_by=request.user,
            **validated_data,
        )
        capacity_resource.dashboards.add(*dashboards)
        return capacity_resource

    @typing.override
    def update(self, instance: CapacityAndResource, validated_data: dict[str, typing.Any]) -> CapacityAndResource:
        dashboards = validated_data.pop("dashboards", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if dashboards is not None:
            instance.dashboards.set(dashboards)
        return instance
