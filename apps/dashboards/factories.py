from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.users.factories import UserFactory

from .models import ExternalDashboard


class ExternalDashboardFactory(DjangoModelFactory[ExternalDashboard]):
    title = Sequence(lambda n: f"Dashboard {n}")
    url = Sequence(lambda n: f"https://app.powerbi.com/embed/{n}")
    page = ExternalDashboard.Page.HOME
    order = Sequence(lambda n: n)
    is_active = True
    created_by = SubFactory(UserFactory)

    class Meta:  # type: ignore[misc]
        model = ExternalDashboard
