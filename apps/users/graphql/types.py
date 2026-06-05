import strawberry
import strawberry_django

from apps.users.models import User, UserRole


@strawberry_django.type(User)
class UserType:
    id: strawberry.ID
    email: strawberry.auto
    full_name: strawberry.auto
    role: UserRole
    region_id: strawberry.ID | None

    @strawberry.field
    def role_display(self) -> str:
        return self.get_role_display()  # type: ignore[reportAttributeAccessIssue]

    is_active: strawberry.auto
    mfa_enabled: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.type(User)
class UserMeType(UserType): ...
