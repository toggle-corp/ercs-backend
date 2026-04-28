from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.users.factories import UserFactory

from .models import Report


class ReportFactory(DjangoModelFactory[Report]):
    title = Sequence(lambda n: f"Report {n}")
    content_type = Report.ContentType.IFRAME
    iframe_url = Sequence(lambda n: f"https://example.com/embed/{n}")
    visibility = Report.Visibility.PUBLIC
    uploaded_by = SubFactory(UserFactory)

    class Meta:  # type: ignore[misc]
        model = Report


class FileReportFactory(ReportFactory):
    content_type = Report.ContentType.FILE
    iframe_url = None
