import strawberry
import strawberry_django
from django.db.models import Q

from apps.users.models import User, UserRole


@strawberry_django.filters.filter(User, lookups=True)
class UserFilter:
    id: strawberry.ID | None = strawberry.UNSET
    role: UserRole | None = strawberry.UNSET
    is_active: bool | None = strawberry.UNSET

    @strawberry_django.filter_field
    def search(self, value: str, prefix: str) -> Q:
        return Q(full_name__icontains=value) | Q(email__icontains=value)

    @strawberry_django.filter_field
    def regions(self, queryset, value: list[strawberry.ID], prefix: str) -> Q:
        return Q(region_id__in=value)
