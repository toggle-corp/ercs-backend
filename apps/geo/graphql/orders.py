import strawberry
import strawberry_django

from apps.geo.models import AdminArea


@strawberry_django.order_type(AdminArea)
class AdminAreaOrder:
    name: strawberry.auto
    level: strawberry.auto
