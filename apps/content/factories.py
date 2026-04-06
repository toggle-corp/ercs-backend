import typing

from factory import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.users.factories import UserFactory

from .models import NewsPost, NewsPostReport


class NewsPostFactory(DjangoModelFactory):
    title = Sequence(lambda n: f"News Post {n}")
    content = "Default content in **markdown**."
    author = SubFactory(UserFactory)
    is_published = False

    class Meta:
        model = NewsPost


class NewsPostReportFactory(DjangoModelFactory):
    order = Sequence(lambda n: n)

    class Meta:
        model = NewsPostReport


if typing.TYPE_CHECKING:
    NewsPostFactory: type[DjangoModelFactory[NewsPost]]
    NewsPostReportFactory: type[DjangoModelFactory[NewsPostReport]]
