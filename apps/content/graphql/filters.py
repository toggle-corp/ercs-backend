import typing

import strawberry
import strawberry_django

from apps.content.models import NewsPost


@strawberry_django.filters.filter(NewsPost, lookups=True)
class NewsPostFilter:
    id: strawberry.ID | None = strawberry.UNSET
    is_published: bool | None = strawberry.UNSET
    author_id: strawberry.ID | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, queryset: typing.Any, value: str, prefix: str) -> typing.Any:
        return queryset.filter(title__icontains=value)
