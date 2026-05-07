import typing

from strawberry.permission import BasePermission
from strawberry.types import Info

from apps.users.models import UserRole


class IsAuthenticated(BasePermission):
    message = "User is not authenticated."

    @typing.override
    def has_permission(self, source: typing.Any, info: Info, **_: typing.Any) -> bool:
        user = info.context.request.user
        return bool(user and user.is_authenticated)


class IsStaffOrAbove(BasePermission):
    message = "Insufficient permissions."

    @typing.override
    def has_permission(self, source: typing.Any, info: Info, **_: typing.Any) -> bool:
        user = info.context.request.user
        if not (user and user.is_authenticated):
            return False
        return user.role in [UserRole.STAFF, UserRole.REGIONAL_ADMIN, UserRole.SUPER_ADMIN]


class IsSuperAdmin(BasePermission):
    message = "Super admin access required."

    @typing.override
    def has_permission(self, source: typing.Any, info: Info, **_: typing.Any) -> bool:
        user = info.context.request.user
        if not (user and user.is_authenticated):
            return False
        return user.role == UserRole.SUPER_ADMIN
