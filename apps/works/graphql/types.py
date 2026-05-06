import strawberry
import strawberry_django

from apps.works.models import EmergencyAlert, EmergencyAlertIframeUrl
from utils.graphql.types import DjangoFileType


@strawberry_django.type(EmergencyAlertIframeUrl)
class EmergencyAlertIframeUrlType:
    id: strawberry.ID
    url: strawberry.auto
    order: strawberry.auto


@strawberry_django.type(EmergencyAlert)
class EmergencyAlertType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    content_type: int
    file: DjangoFileType | None
    iframe_urls: list[EmergencyAlertIframeUrlType]
    is_published: strawberry.auto
    published_at: strawberry.auto
    uploaded_by_id: strawberry.ID
    region_id: strawberry.ID | None
    created_at: strawberry.auto
    updated_at: strawberry.auto
