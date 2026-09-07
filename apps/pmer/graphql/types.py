import strawberry
import strawberry_django
from django.db import models
from strawberry.types import Info

from apps.geo.graphql.types import AdminAreaType
from apps.pmer.models import PmerReport, PmerReportCategory, PmerReportDocumentType
from apps.reports.models import ReportVisibility
from apps.users.graphql.types import UserType
from utils.graphql.types import DjangoFileType


@strawberry_django.type(PmerReport)
class PmerReportType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    file: DjangoFileType
    category: PmerReportCategory
    report_type: PmerReportDocumentType
    created_by: UserType
    created_at: strawberry.auto
    updated_at: strawberry.auto
    region: AdminAreaType | None
    department: strawberry.auto
    project: strawberry.auto
    visibility: ReportVisibility

    @strawberry.field
    def category_display(self) -> str:
        return self.get_category_display()  # type: ignore[reportAttributeAccessIssue]

    @strawberry.field
    def report_type_display(self) -> str:
        return self.get_report_type_display()  # type: ignore[reportAttributeAccessIssue]

    @strawberry.field
    def visibility_display(self) -> str:
        return self.get_visibility_display()  # type: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_queryset(cls, queryset: models.QuerySet[PmerReport], info: Info) -> models.QuerySet[PmerReport]:
        user = info.context.request.user
        if user and user.is_authenticated:
            return queryset
        return queryset.filter(visibility=ReportVisibility.PUBLIC)
