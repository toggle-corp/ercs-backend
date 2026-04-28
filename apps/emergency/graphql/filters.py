import typing

import strawberry
import strawberry_django

from apps.emergency.models import Emergency


@strawberry_django.filters.filter(Emergency, lookups=True)
class EmergencyFilter:
    id: strawberry.ID | None = strawberry.UNSET
    disaster_type: str | None = strawberry.UNSET
    status: str | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET
    go_id: int | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, queryset: typing.Any, value: str, prefix: str) -> typing.Any:
        return queryset.filter(name__icontains=value)
