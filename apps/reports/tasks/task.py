from celery import Task
from celery.utils.log import get_task_logger

from apps.reports.ai_features.extraction import PdfExtraction
from apps.reports.models import Report
from main.celery import app

logger = get_task_logger(__name__)


@app.task(bind=True)
def handle_documents(celery_task: Task, report_id: int, pdf_bytes: bytes):
    report = Report.objects.filter(pk=report_id).first()
    if report:
        ext = PdfExtraction(report=report, source_file_path=pdf_bytes)
        ext.pdf_to_images()
    else:
        logger.warning("Report with id: %s not found", str(report_id))
