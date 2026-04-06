import strawberry
import strawberry_django

from apps.emergency.models import Emergency


@strawberry_django.type(Emergency)
class EmergencyType:
    id: strawberry.ID
    go_id: strawberry.auto
    name: strawberry.auto
    disaster_type: strawberry.auto
    status: strawberry.auto
    region_id: strawberry.ID | None
    start_date: strawberry.auto
    affected_pop: strawberry.auto
    go_url: strawberry.auto
    synced_at: strawberry.auto
