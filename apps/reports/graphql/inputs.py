import strawberry
from strawberry.file_uploads import Upload

from apps.reports.models import ReportType, ReportVisibility


@strawberry.input
class LinkCreateInput:
    title: str
    url: str
    link_type: int
    description: str | None = strawberry.UNSET


@strawberry.input
class LinkUpdateInput:
    title: str | None = strawberry.UNSET
    url: str | None = strawberry.UNSET
    link_type: int | None = strawberry.UNSET
    description: str | None = strawberry.UNSET


@strawberry.input
class ReportCreateInput:
    title: str
    content_type: int
    description: str | None = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET
    file: Upload | None = strawberry.UNSET
    iframe_url: str | None = strawberry.UNSET
    visibility: int = ReportVisibility.PUBLIC
    report_type: int = ReportType.REPORT
    thematic_area: strawberry.ID
    region: strawberry.ID | None = strawberry.UNSET
    disaster_type: str | None = strawberry.UNSET
    owner: str | None = strawberry.UNSET
    published_at: str | None = strawberry.UNSET


@strawberry.input
class ReportUpdateInput:
    title: str | None = strawberry.UNSET
    description: str | None = strawberry.UNSET
    cover_image: Upload | None = strawberry.UNSET
    file: Upload | None = strawberry.UNSET
    visibility: int | None = strawberry.UNSET
    report_type: int | None = strawberry.UNSET
    thematic_area: strawberry.ID | None = strawberry.UNSET
    region: strawberry.ID | None = strawberry.UNSET
    disaster_type: str | None = strawberry.UNSET
    owner: str | None = strawberry.UNSET
    published_at: str | None = strawberry.UNSET
