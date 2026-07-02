import strawberry
import strawberry_django
from asgiref.sync import sync_to_async

from apps.reports.models import (
    DocumentExtraction,
    DocumentExtractionStatus,
    Link,
    Report,
    ReportContentType,
    ReportVisibility,
    ThematicArea,
)
from apps.reports.models import LinkType as LinkTypeEnum
from apps.reports.models import ReportType as ReportTypeEnum
from utils.graphql.types import DjangoFileType

# Register collision-prone enums under distinct GraphQL names before the
# @strawberry_django.type decorators below process the field annotations.
# Without this, strawberry would auto-register both as "LinkType"/"ReportType",
# clashing with the object types of the same name defined in this file.
strawberry.enum(LinkTypeEnum, name="LinkTypeEnum")
strawberry.enum(ReportTypeEnum, name="ReportTypeEnum")


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
    thematic_area_id: strawberry.ID | None

    @strawberry.field
    def content_type_display(self) -> str:
        return self.get_content_type_display()  # type: ignore[reportAttributeAccessIssue]

    @strawberry.field
    def visibility_display(self) -> str:
        return self.get_visibility_display()  # type: ignore[reportAttributeAccessIssue]

    @strawberry.field
    @sync_to_async
    def report_type_display(self) -> str:
        return self.get_report_type_display()  # type: ignore[reportAttributeAccessIssue]

    region_id: strawberry.ID | None
    disaster_type: strawberry.auto
    owner: strawberry.auto
    uploaded_by_id: strawberry.ID
    published_at: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto


@strawberry_django.type(DocumentExtraction)
class ReportSummaryType:
    id: strawberry.ID
    report: strawberry.auto
    text: strawberry.auto
    page_number: strawberry.auto
    chunk_type: DocumentExtraction.ExtractionType
    status: DocumentExtractionStatus
