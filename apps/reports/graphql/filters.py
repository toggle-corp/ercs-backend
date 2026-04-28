import typing

import strawberry
import strawberry_django

from apps.reports.models import Report, ThematicArea


@strawberry_django.filters.filter(ThematicArea, lookups=True)
class ThematicAreaFilter:
    id: strawberry.ID | None = strawberry.UNSET
    name: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, queryset: typing.Any, value: str, prefix: str) -> typing.Any:
        return queryset.filter(name__icontains=value)


@strawberry_django.filters.filter(Report, lookups=True)
class ReportFilter:
    id: strawberry.ID | None = strawberry.UNSET
    content_type: int | None = strawberry.UNSET
    visibility: int | None = strawberry.UNSET
    thematic_area_id: strawberry.ID | None = strawberry.UNSET
    region_id: strawberry.ID | None = strawberry.UNSET
    disaster_type: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, queryset: typing.Any, value: str, prefix: str) -> typing.Any:
        return queryset.filter(title__icontains=value)
