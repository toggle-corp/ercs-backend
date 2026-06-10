"""AI document extraction trigger for REPORT-type reports."""

import logging

from apps.reports.models import Report
from django.core.files.storage import default_storage
from apps.reports.tasks.task import handle_documents

logger = logging.getLogger(__name__)


async def trigger_document_extraction(report: Report) -> None:
    """Create or reset the DocumentExtraction record and dispatch to the AI tool.

    Called after a REPORT-type report is created or its file is replaced.
    The AI tool is expected to update extracted_contents, search_text, summary,
    and status directly in the database once processing completes.
    """

    #await DocumentExtraction.objects.aupdate_or_create(
    #    report=report,
    #    defaults={
    #        "status": DocumentExtractionStatus.PENDING,
    #        "text": "",
    #        "page_number": 0,
    #        "chunk_type": DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY,
    #    },
    #)


    #file_path = report.file.name if report.file else ""
    #report_id: str = str(report.pk)
    with default_storage.open(report.file.name, "rb") as f:
        pdf_bytes = f.read()
    logger.info("Triggering document extraction for report_id=%s file_path=%s",report.file.name, str(report.pk)) #report_id, file_path)

    # TODO: Send extraction request to AI tool.
    # Example payload: {"report_id": report_id, "file_path": file_path}
    handle_documents.delay(report.pk, pdf_bytes)
    # Move the LLM part to another file
