"""AI document extraction trigger for REPORT-type reports."""

import logging

from .models import DocumentExtraction, DocumentExtractionStatus, Report

logger = logging.getLogger(__name__)


async def trigger_document_extraction(report: Report) -> None:
    """Create or reset the DocumentExtraction record and dispatch to the AI tool.

    Called after a REPORT-type report is created or its file is replaced.
    The AI tool is expected to update extracted_contents, search_text, summary,
    and status directly in the database once processing completes.
    """
    await DocumentExtraction.objects.aupdate_or_create(
        report=report,
        defaults={
            "status": DocumentExtractionStatus.PENDING,
            "extracted_contents": None,
            "search_text": "",
            "summary": "",
        },
    )

    file_path = report.file.name if report.file else ""
    report_id: str = str(report.pk)

    logger.info("Triggering document extraction for report_id=%s file_path=%s", report_id, file_path)

    # TODO: Send extraction request to AI tool.
    # Example payload: {"report_id": report_id, "file_path": file_path}
