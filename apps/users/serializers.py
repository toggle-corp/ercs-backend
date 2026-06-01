import typing

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["email", "full_name", "role", "region", "is_active", "password"]

    @typing.override
    def create(self, validated_data: dict[str, typing.Any]) -> User:
        password = validated_data.pop("password", None)
        return User.objects.create_user(password=password or "", **validated_data)  # type: ignore[reportAttributeAccessIssue]

    @typing.override
    def update(self, instance: User, validated_data: dict[str, typing.Any]) -> User:
        validated_data.pop("password", None)
        return super().update(instance, validated_data)
