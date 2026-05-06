import strawberry
import strawberry_django
from strawberry_django.pagination import OffsetPaginated

from .filters import EmergencyAlertFilter
from .orders import EmergencyAlertOrder
from .types import EmergencyAlertType


@strawberry.type
class Query:
    EmergencyAlerts: OffsetPaginated[EmergencyAlertType] = strawberry_django.offset_paginated(
        filters=EmergencyAlertFilter,
        order=EmergencyAlertOrder,
    )

    EmergencyAlert: EmergencyAlertType = strawberry_django.field()
