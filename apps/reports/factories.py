from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.users.factories import UserFactory

from .models import Report, ThematicArea


class ThematicAreaFactory(DjangoModelFactory[ThematicArea]):
    name = Sequence(lambda n: f"Thematic Area {n}")

    class Meta:  # type: ignore[misc]
        model = ThematicArea


class ReportFactory(DjangoModelFactory[Report]):
    title = Sequence(lambda n: f"Report {n}")
    content_type = Report.ContentType.IFRAME
    iframe_url = Sequence(lambda n: f"https://example.com/embed/{n}")
    visibility = Report.Visibility.PUBLIC
    uploaded_by = SubFactory(UserFactory)
    thematic_area = SubFactory(ThematicAreaFactory)

    class Meta:  # type: ignore[misc]
        model = Report


class FileReportFactory(ReportFactory):
    content_type = Report.ContentType.FILE
    iframe_url = None
