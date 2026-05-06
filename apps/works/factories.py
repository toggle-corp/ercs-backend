from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.common.models import ContentType
from apps.users.factories import UserFactory

from .models import EmergencyAlert


class EmergencyAlertFactory(DjangoModelFactory[EmergencyAlert]):
    title = Sequence(lambda n: f"EmergencyAlert {n}")
    content_type = ContentType.IFRAME
    iframe_url = Sequence(lambda n: f"https://example.com/embed/{n}")
    is_published = False
    uploaded_by = SubFactory(UserFactory)

    class Meta:  # type: ignore[misc]
        model = EmergencyAlert


class FileEmergencyAlertFactory(EmergencyAlertFactory):
    content_type = ContentType.FILE
    iframe_url = None
