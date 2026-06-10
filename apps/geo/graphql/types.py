import strawberry
import strawberry_django

from apps.geo.models import AdminArea, AdminAreaLevel


@strawberry_django.type(AdminArea)
class AdminAreaType:
    id: strawberry.ID
    name: strawberry.auto
    name_am: strawberry.auto
    level: AdminAreaLevel
    parent_id: strawberry.ID | None

    @strawberry.field
    def level_display(self) -> str:
        return self.get_level_display()  # type: ignore[reportAttributeAccessIssue]

    pcode: strawberry.auto
    centroid_lat: strawberry.auto
    centroid_lon: strawberry.auto
