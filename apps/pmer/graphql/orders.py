import strawberry
import strawberry_django

from apps.pmer.models import PmerReport


@strawberry_django.order_type(PmerReport)
class PmerReportOrder:
    title: strawberry.auto
