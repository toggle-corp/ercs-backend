import strawberry
from strawberry.file_uploads import Upload

from apps.reports.models import ReportVisibility


@strawberry.input
class ReportCreateInput:
    title: str
    content_type: int
    description: str | None = strawberry.UNSET
    file: Upload | None = strawberry.UNSET
    iframe_url: str | None = strawberry.UNSET
    visibility: int = ReportVisibility.PUBLIC
    thematic_area: strawberry.ID
    region: strawberry.ID | None = strawberry.UNSET
    disaster_type: str | None = strawberry.UNSET
    owner: str | None = strawberry.UNSET
    published_at: str | None = strawberry.UNSET


@strawberry.input
class ReportUpdateInput:
    title: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    visibility: int | None = strawberry.UNSET
    thematic_area: strawberry.ID | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    disaster_type: str | None = strawberry.UNSET
    owner: str | None = strawberry.UNSET
    published_at: str | None = strawberry.UNSET
