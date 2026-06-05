import strawberry
import strawberry_django

from apps.reports.models import Link, Report, ReportContentType, ReportVisibility, ThematicArea
from apps.reports.models import LinkType as LinkTypeEnum
from apps.reports.models import ReportType as ReportTypeEnum
from utils.graphql.types import DjangoFileType


@strawberry_django.type(Link)
class LinkType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    url: strawberry.auto
    link_type: LinkTypeEnum
    created_at: strawberry.auto
    updated_at: strawberry.auto

    @strawberry.field
    def link_type_display(self) -> str:
        return self.get_link_type_display()  # type: ignore[reportAttributeAccessIssue]


@strawberry_django.type(ThematicArea)
class ThematicAreaType:
    id: strawberry.ID
    name: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto


@strawberry_django.type(Report)
class ReportType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    cover_image: DjangoFileType | None
    content_type: ReportContentType
    file: DjangoFileType | None
    iframe_url: strawberry.auto
    visibility: ReportVisibility
    report_type: ReportTypeEnum
    thematic_area_id: strawberry.ID

    @strawberry.field
    def content_type_display(self) -> str:
        return self.get_content_type_display()  # type: ignore[reportAttributeAccessIssue]

    @strawberry.field
    def visibility_display(self) -> str:
        return self.get_visibility_display()  # type: ignore[reportAttributeAccessIssue]

    @strawberry.field
    def report_type_display(self) -> str:
        return self.get_report_type_display()  # type: ignore[reportAttributeAccessIssue]

    region_id: strawberry.ID | None
    disaster_type: strawberry.auto
    owner: strawberry.auto
    uploaded_by_id: strawberry.ID
    published_at: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto
