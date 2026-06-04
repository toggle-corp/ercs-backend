import strawberry

from apps.users.models import UserRole


@strawberry.input
class UserCreateInput:
    email: str
    full_name: str
    password: str
    role: int = UserRole.VIEWER
    region: strawberry.ID | None = strawberry.UNSET
    is_active: bool = True


@strawberry.input
class UserUpdateInput:
    full_name: str | None = strawberry.UNSET
    role: int | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET


@strawberry.input
class PasswordUpdateInput:
    current_password: str
    new_password: str
