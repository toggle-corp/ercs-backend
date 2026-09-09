import strawberry
import strawberry_django
from strawberry.file_uploads import Upload

from apps.pmer.models import PmerReport, PmerReportCategory, PmerReportDocumentType
from apps.reports.models import ReportVisibility


@strawberry_django.input(PmerReport)
class PmerReportCreateInput:
    title: strawberry.auto
    category: PmerReportCategory
    report_type: PmerReportDocumentType
    file: Upload
    description: strawberry.auto
    department: strawberry.auto
    project: strawberry.auto
    region: strawberry.ID | None = strawberry.UNSET
    visibility: ReportVisibility = ReportVisibility.PUBLIC


@strawberry_django.partial(PmerReport)
class PmerReportUpdateInput:
    title: strawberry.auto
    # `strawberry.auto` cannot resolve an IntegerChoicesField to a registered
    # GraphQL enum, so the choices enum is named explicitly here.
    category: PmerReportCategory | None = strawberry.UNSET
    report_type: PmerReportDocumentType | None = strawberry.UNSET
    file: Upload | None = strawberry.UNSET
    description: strawberry.auto
    department: strawberry.auto
    project: strawberry.auto
    region: strawberry.ID | None = strawberry.UNSET
    visibility: ReportVisibility | None = strawberry.UNSET
