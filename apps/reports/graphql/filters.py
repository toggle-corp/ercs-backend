import strawberry
import strawberry_django
from django.db.models import Q

from apps.reports.models import Link, Report, ThematicArea


@strawberry_django.filters.filter(Link, lookups=True)
class LinkFilter:
    id: strawberry.ID | None = strawberry.UNSET
    link_type: int | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value) | Q(description__icontains=value)


@strawberry_django.filters.filter(ThematicArea, lookups=True)
class ThematicAreaFilter:
    id: strawberry.ID | None = strawberry.UNSET
    name: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(name__icontains=value)


@strawberry_django.filters.filter(Report, lookups=True)
class ReportFilter:
    id: strawberry.ID | None = strawberry.UNSET
    content_type: int | None = strawberry.UNSET
    visibility: int | None = strawberry.UNSET
    thematic_area_id: strawberry.ID | None = strawberry.UNSET
    disaster_type: str | None = strawberry.UNSET
    report_type: str | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(title__icontains=value)

    @strawberry_django.filter_field
    def regions(self, queryset, value: list[strawberry.ID], prefix: str) -> Q:
        return Q(region_id__in=value)
