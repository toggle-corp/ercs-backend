import strawberry
import strawberry_django

from apps.pmer.models import PmerReport, PmerReportCategory, PmerReportDocumentType
from apps.reports.models import ReportVisibility


@strawberry_django.filters.filter(PmerReport, lookups=True)
class PmerReportFilter:
    id: strawberry.ID | None = strawberry.UNSET
    category: PmerReportCategory | None = strawberry.UNSET
    report_type: PmerReportDocumentType | None = strawberry.UNSET
    title: strawberry.auto
    department: strawberry.auto
    project: strawberry.auto
    region_id: strawberry.ID | None = strawberry.UNSET
    visibility: ReportVisibility | None = strawberry.UNSET
