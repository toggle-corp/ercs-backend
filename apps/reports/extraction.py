"""AI document extraction trigger for REPORT-type reports."""

import logging

from django.core.files.storage import default_storage

from apps.reports.models import Report
from apps.reports.tasks.task import handle_documents

logger = logging.getLogger(__name__)


async def trigger_document_extraction(report: Report) -> None:
    """Create or reset the DocumentExtraction record and dispatch to the AI tool.

    Called after a REPORT-type report is created or its file is replaced.
    The AI tool is expected to update extracted_contents, search_text, summary,
    and status directly in the database once processing completes.
    """
    if not report.file.name:
        logger.warning("Report file is missing")
        return

    with default_storage.open(report.file.name, "rb") as f:
        pdf_bytes = f.read()
    logger.info(
        "Triggering document extraction for report_id=%s file_path=%s",
        str(report.pk),
        report.file.name,
    )
    handle_documents.apply_async(args=[report.pk, pdf_bytes])  # pyright: ignore[reportFunctionMemberAccess]
