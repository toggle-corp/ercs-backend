import strawberry
import strawberry_django

from apps.works.models import EmergencyAlert


@strawberry_django.order_type(EmergencyAlert)
class EmergencyAlertOrder:
    title: strawberry.auto
    created_at: strawberry.auto
    published_at: strawberry.auto
