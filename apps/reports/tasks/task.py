import logging

from celery import shared_task
from django.core.files.storage import default_storage

from apps.reports.ai_features.extraction import PdfExtraction
from apps.reports.models import Report

logger = logging.getLogger(__name__)


@shared_task
def handle_documents(report_id: int) -> None:
    report = Report.objects.filter(pk=report_id).first()

    if report is None or report.file.name is None:
        logger.warning("Report with id %s is set to None", report_id)
        return

    with default_storage.open(report.file.name, "rb") as f:
        pdf_bytes = f.read()

    ext = PdfExtraction(
        report=report,
        data=pdf_bytes,
    )
    ext.pdf_to_images()
