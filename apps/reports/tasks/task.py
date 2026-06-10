from celery import shared_task
from celery.utils.log import get_task_logger
from celery import Task
from main.celery import app
from apps.reports.summarization import PdfExtraction

from apps.reports.models import Report


logger = get_task_logger(__name__)

@app.task(bind=True)
def handle_documents(celery_task: Task, report_id: int, pdf_bytes: bytes):
    logger.info(f"hello, i am running from the task {str(report_id)}")

    report = Report.objects.filter(pk=report_id).first()

    if report:
        ext = PdfExtraction(report=report, source_file_path=pdf_bytes)
        ext.pdf_to_images()
