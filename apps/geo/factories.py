from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from .models import AdminArea


class AdminAreaFactory(DjangoModelFactory[AdminArea]):
    name = Sequence(lambda n: f"Area {n}")
    level = AdminArea.Level.REGION
    parent = None

    class Meta:  # type: ignore[misc]
        model = AdminArea


class CountryFactory(AdminAreaFactory):
    name = Sequence(lambda n: f"Country {n}")
    level = AdminArea.Level.COUNTRY
    parent = None


class RegionFactory(AdminAreaFactory):
    name = Sequence(lambda n: f"Region {n}")
    level = AdminArea.Level.REGION
    parent = SubFactory(CountryFactory)


class ZoneFactory(AdminAreaFactory):
    name = Sequence(lambda n: f"Zone {n}")
    level = AdminArea.Level.ZONE
    parent = SubFactory(RegionFactory)


class WoredaFactory(AdminAreaFactory):
    name = Sequence(lambda n: f"Woreda {n}")
    level = AdminArea.Level.WOREDA
    parent = SubFactory(ZoneFactory)
