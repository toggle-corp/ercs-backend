import logging

from celery import shared_task
from django.core.files.storage import default_storage

from apps.reports.ai_features.extraction import HeaderExtraction, PdfExtraction
from apps.reports.models import DocumentExtraction, Report, ReportContentType

logger = logging.getLogger(__name__)


@shared_task
def handle_documents(report_id: int, report_type: ReportContentType) -> None:
    report = Report.objects.filter(pk=report_id).first()

    if report is None:
        logger.warning("Report with id %s not found", report_id)
        return

    if report_type == ReportContentType.FILE and report.file.name is None:
        logger.warning("Report with id %s has no file", report_id)
        return

    # Re-extraction (e.g. after a report edit/file replace) must start clean, otherwise
    # Any previous report entries will be delete and start fresh.
    DocumentExtraction.objects.filter(report=report).delete()

    if report.file and (file_name := report.file.name) and report_type == ReportContentType.FILE:
        with default_storage.open(file_name, "rb") as f:
            pdf_bytes = f.read()

        ext = PdfExtraction(
            report=report,
            data=pdf_bytes,
        )
        ext.pdf_to_images()
    elif report_type == ReportContentType.IFRAME:
        ext = HeaderExtraction(report=report)
        ext.handle_meta_info()
