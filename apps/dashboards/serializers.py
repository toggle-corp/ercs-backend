import typing

from rest_framework import serializers

from apps.geo.models import AdminArea

from .models import CapacityAndResource, DashboardPage, ExternalDashboard


class ExternalDashboardSerializer(serializers.ModelSerializer):
    capacity_and_resource = serializers.PrimaryKeyRelatedField(
        queryset=CapacityAndResource.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ExternalDashboard
        fields = [
            "title",
            "description",
            "url",
            "page",
            "region",
            "capacity_and_resource",
            "show_on_home",
            "order",
            "is_active",
            "created_by",
        ]
        extra_kwargs = {
            "created_by": {"required": False},
        }

    HOME_DASHBOARD_LIMIT = 6

    @typing.override
    def validate(self, data: dict) -> dict:  # type: ignore[reportIncompatibleMethodOverride]
        # Home dashboard limit validation
        if data.get("show_on_home"):
            qs = ExternalDashboard.objects.filter(show_on_home=True)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.count() >= self.HOME_DASHBOARD_LIMIT:
                raise serializers.ValidationError(
                    {
                        "show_on_home": (
                            f"Maximum of {self.HOME_DASHBOARD_LIMIT} dashboards can be shown on the home page."
                        ),
                    },
                )

        # Capacity & Resource validation
        instance = self.instance
        capacity_and_resource = data.get(
            "capacity_and_resource",
            getattr(instance, "capacity_and_resource", None),
        )
        page = data.get("page", getattr(instance, "page", None))

        if capacity_and_resource is not None and page != DashboardPage.CAPACITY_RESOURCES:
            raise serializers.ValidationError(
                {
                    "capacity_and_resource": (
                        "Only dashboards with page CAPACITY_RESOURCES can be linked to a Capacity & Resource entry."
                    ),
                },
            )
        return data

    @typing.override
    def create(self, validated_data: dict) -> ExternalDashboard:
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data.setdefault("created_by", request.user)
        return super().create(validated_data)


class CapacityAndResourceSerializer(serializers.ModelSerializer):
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
        ]

    @typing.override
    def create(self, validated_data: dict[str, typing.Any]) -> CapacityAndResource:
        request = self.context["request"]
        return CapacityAndResource.objects.create(
            created_by=request.user,
            **validated_data,
        )

    @typing.override
    def update(self, instance: CapacityAndResource, validated_data: dict[str, typing.Any]) -> CapacityAndResource:
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
