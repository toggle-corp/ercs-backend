import strawberry
import strawberry_django

from apps.reports.models import Report


@strawberry_django.order_type(Report)
class ReportOrder:
    title: strawberry.auto
    created_at: strawberry.auto
    published_at: strawberry.auto
