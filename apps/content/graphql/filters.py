import strawberry
import strawberry_django
from django.db.models import Q

from apps.content.models import NewsPost


@strawberry_django.filters.filter(NewsPost, lookups=True)
class NewsPostFilter:
    id: strawberry.ID | None = strawberry.UNSET
    is_published: bool | None = strawberry.UNSET
    author_id: strawberry.ID | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)
