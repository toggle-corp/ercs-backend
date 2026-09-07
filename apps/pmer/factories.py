from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory, FileField

from apps.users.factories import UserFactory

from .models import PmerReport


class PmerReportFactory(DjangoModelFactory[PmerReport]):
    title = Sequence(lambda n: f"PMER Report {n}")
    description = Sequence(lambda n: f"PMER report description {n}")
    file = FileField(filename="pmer-report.pdf")
    category = PmerReport.Category.DPR
    report_type = PmerReport.DocumentType.ANNUAL_REPORT
    visibility = PmerReport.Visibility.PUBLIC
    created_by = SubFactory(UserFactory)

    class Meta:  # type: ignore[misc]
        model = PmerReport
