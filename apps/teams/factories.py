from factory.declarations import Sequence
from factory.django import DjangoModelFactory

from .models import Team


class TeamFactory(DjangoModelFactory[Team]):
    name = Sequence(lambda n: f"Team {n}")

    class Meta:  # type: ignore[misc]
        model = Team
