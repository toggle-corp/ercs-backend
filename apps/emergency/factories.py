import datetime

from factory.declarations import Sequence
from factory.django import DjangoModelFactory

from .models import Emergency


class EmergencyFactory(DjangoModelFactory[Emergency]):
    go_id = Sequence(lambda n: n + 1000)
    name = Sequence(lambda n: f"Emergency {n}")
    disaster_type = "Flood"
    status = "Active"
    start_date = datetime.date(2024, 1, 1)

    class Meta:  # type: ignore[misc]
        model = Emergency
