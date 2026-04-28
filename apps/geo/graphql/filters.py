import typing

import strawberry
import strawberry_django

from apps.geo.models import AdminArea


@strawberry_django.filters.filter(AdminArea, lookups=True)
class AdminAreaFilter:
    id: strawberry.ID | None = strawberry.UNSET
    level: str | None = strawberry.UNSET
    parent_id: strawberry.ID | None = strawberry.UNSET
    pcode: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, queryset: typing.Any, value: str, prefix: str) -> typing.Any:
        return queryset.filter(name__icontains=value)
