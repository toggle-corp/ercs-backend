import typing

from factory import Sequence
from factory.django import DjangoModelFactory

from .models import Team


class TeamFactory(DjangoModelFactory):
    name = Sequence(lambda n: f"Team {n}")
    team_type = "BDRT"

    class Meta:
        model = Team


if typing.TYPE_CHECKING:
    TeamFactory: type[DjangoModelFactory[Team]]
