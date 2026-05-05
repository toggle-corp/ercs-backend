import strawberry
import strawberry_django

from apps.resources.models import Resource, ResourceIframeUrl
from utils.graphql.types import DjangoFileType


@strawberry_django.type(ResourceIframeUrl)
class ResourceIframeUrlType:
    id: strawberry.ID
    url: strawberry.auto


@strawberry_django.type(Resource)
class ResourceType:
    id: strawberry.ID
    title: strawberry.auto
    description: strawberry.auto
    content_type: int
    file: DjangoFileType | None
    iframe_urls: list[ResourceIframeUrlType]
    is_published: strawberry.auto
    published_at: strawberry.auto
    uploaded_by_id: strawberry.ID
    region_id: strawberry.ID | None
    created_at: strawberry.auto
    updated_at: strawberry.auto