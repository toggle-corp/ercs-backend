from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.users.factories import UserFactory

from .models import Resource


class ResourceFactory(DjangoModelFactory[Resource]):
    title = Sequence(lambda n: f"Resource {n}")
    content_type = Resource.ContentType.IFRAME
    iframe_url = Sequence(lambda n: f"https://example.com/embed/{n}")
    is_published = False
    uploaded_by = SubFactory(UserFactory)

    class Meta:  # type: ignore[misc]
        model = Resource


class FileResourceFactory(ResourceFactory):
    content_type = Resource.ContentType.FILE
    iframe_url = None