import strawberry
from strawberry.types import Info
from strawberry_django.auth.mutations import resolve_login, resolve_logout
from strawberry_django.resolvers import django_resolver

from .types import UserMeType


# NOTE:
# resolve_login accepts a username kwarg, but Django's authentication backend resolves
# credentials via USERNAME_FIELD which is set to "email" on our User model so passing the email as username works correctly.
# django_resolver ensures synchronous ORM calls (authenticate,login, session writes)
# are safe in both WSGI and ASGI execution contexts.
@strawberry.type
class Mutation:
    @strawberry.mutation
    @django_resolver
    def login(self, info: Info, email: str, password: str) -> UserMeType:
        return resolve_login(info, username=email, password=password)  # type: ignore[reportReturnType]

    @strawberry.mutation
    @django_resolver
    def logout(self, info: Info) -> bool:
        return resolve_logout(info)  # type: ignore[reportReturnType]
