import logging

from celery import shared_task

from apps.reports.ai_features.extraction import PdfExtraction
from apps.reports.models import Report

logger = logging.getLogger(__name__)


@shared_task
def handle_documents(report_id: int, pdf_bytes: bytes) -> None:
    report = Report.objects.filter(pk=report_id).first()

    if report is None:
        logger.warning("Report with id %s not found", report_id)
        return

    ext = PdfExtraction(
        report=report,
        data=pdf_bytes,
    )
    ext.pdf_to_images()
