import strawberry
import strawberry_django

from apps.content.models import NewsPost


@strawberry_django.order_type(NewsPost)
class NewsPostOrder:
    title: strawberry.auto
    created_at: strawberry.auto
    published_at: strawberry.auto
