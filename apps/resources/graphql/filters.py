import strawberry
import strawberry_django
from django.db.models import Q

from apps.resources.models import Resource


@strawberry_django.filters.filter(Resource, lookups=True)
class ResourceFilter:
    id: strawberry.ID | None = strawberry.UNSET
    content_type: int | None = strawberry.UNSET
    is_published: bool | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value) | Q(description__icontains=value)