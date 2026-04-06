import strawberry
import strawberry_django

from apps.geo.models import AdminArea


@strawberry_django.type(AdminArea)
class AdminAreaType:
    id: strawberry.ID
    name: strawberry.auto
    name_am: strawberry.auto
    level: int
    parent_id: strawberry.ID | None
    pcode: strawberry.auto
    centroid_lat: strawberry.auto
    centroid_lon: strawberry.auto
