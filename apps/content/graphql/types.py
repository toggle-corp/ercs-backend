import strawberry
import strawberry_django

from apps.content.models import NewsPost, NewsPostReport
from apps.reports.graphql.types import ReportType
from utils.graphql.types import DjangoFileType


@strawberry_django.type(NewsPost)
class NewsPostType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    cover_image: DjangoFileType | None
    content: strawberry.auto
    author_id: strawberry.ID
    region_id: strawberry.ID | None
    is_published: strawberry.auto
    published_at: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto
    reports: list[ReportType]


@strawberry_django.type(NewsPostReport)
class NewsPostReportType:
    id: strawberry.ID
    newspost_id: strawberry.ID
    report: ReportType
    order: strawberry.auto
