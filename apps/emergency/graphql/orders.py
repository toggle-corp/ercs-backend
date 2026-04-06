import strawberry
import strawberry_django

from apps.emergency.models import Emergency


@strawberry_django.order_type(Emergency)
class EmergencyOrder:
    name: strawberry.auto
    start_date: strawberry.auto
    synced_at: strawberry.auto
