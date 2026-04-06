import strawberry
import strawberry_django

from apps.users.models import User


@strawberry_django.type(User)
class UserType:
    id: strawberry.ID
    email: strawberry.auto
    full_name: strawberry.auto
    role: int
    region_id: strawberry.ID | None
    is_active: strawberry.auto
    mfa_enabled: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.type(User)
class UserMeType(UserType): ...
