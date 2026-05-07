from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.users.factories import UserFactory

from .models import NewsPost, NewsPostReport


class NewsPostFactory(DjangoModelFactory[NewsPost]):
    title = Sequence(lambda n: f"News Post {n}")
    content = "Default content in **markdown**."
    author = SubFactory(UserFactory)
    is_published = False

    class Meta:  # type: ignore[misc]
        model = NewsPost


class NewsPostReportFactory(DjangoModelFactory[NewsPostReport]):
    order = Sequence(lambda n: n)

    class Meta:  # type: ignore[misc]
        model = NewsPostReport
