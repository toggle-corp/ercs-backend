import strawberry
import strawberry_django

from apps.reports.models import Report, ThematicArea
from utils.graphql.types import DjangoFileType


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
    content_type: int
    file: DjangoFileType | None
    iframe_url: strawberry.auto
    visibility: int
    thematic_area_id: strawberry.ID
    region_id: strawberry.ID | None
    disaster_type: strawberry.auto
    owner: strawberry.auto
    uploaded_by_id: strawberry.ID
    published_at: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto
