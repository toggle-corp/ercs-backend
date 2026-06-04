import strawberry
import strawberry_django

from apps.users.models import User


@strawberry_django.order_type(User)
class UserOrder:
    full_name: strawberry.auto
    email: strawberry.auto
    created_at: strawberry.auto
