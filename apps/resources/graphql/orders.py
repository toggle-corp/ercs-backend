# apps/resources/graphql/orders.py
import strawberry
import strawberry_django

from apps.resources.models import Resource


@strawberry_django.order_type(Resource)
class ResourceOrder:
    title: strawberry.auto
    created_at: strawberry.auto
    published_at: strawberry.auto