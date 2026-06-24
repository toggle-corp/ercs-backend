from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from apps.users.factories import UserFactory

from .models import DocumentExtraction, Link, Report, ThematicArea


class ThematicAreaFactory(DjangoModelFactory[ThematicArea]):
    name = Sequence(lambda n: f"Thematic Area {n}")

    class Meta:  # type: ignore[misc]
        model = ThematicArea


class ReportFactory(DjangoModelFactory[Report]):
    title = Sequence(lambda n: f"Report {n}")
    content_type = Report.ContentType.IFRAME
    iframe_url = Sequence(lambda n: f"https://example.com/embed/{n}")
    visibility = Report.Visibility.PUBLIC
    report_type = Report.ReportType.REPORT
    uploaded_by = SubFactory(UserFactory)
    thematic_area = SubFactory(ThematicAreaFactory)

    class Meta:  # type: ignore[misc]
        model = Report


class LinkFactory(DjangoModelFactory[Link]):
    title = Sequence(lambda n: f"Link {n}")
    url = Sequence(lambda n: f"https://example.com/link/{n}")
    link_type = Link.LinkType.EXTERNAL

    class Meta:  # type: ignore[misc]
        model = Link


class FileReportFactory(ReportFactory):
    content_type = Report.ContentType.FILE
    iframe_url = None


class DocumentExtractionFactory(DjangoModelFactory[DocumentExtraction]):
    report = SubFactory(ReportFactory)
    text = Sequence(lambda n: f"Extracted text chunk {n}")
    chunk_type = DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY
    status = DocumentExtraction.Status.PENDING

    class Meta:  # type: ignore[misc]
        model = DocumentExtraction
