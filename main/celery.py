import logging
import os
from logging.config import dictConfig

from banjo_utils.celery_health.worker import setup_worker_heartbeat
from celery import Celery, signals
from celery.schedules import crontab

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

app = Celery("main")
# banjo-utils worker heartbeat writer (read by banjo-celery-probe for k8s liveness).
setup_worker_heartbeat(app)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.task_default_queue = "default"

# Static beat schedule (no django-celery-beat). Times are UTC (settings.TIME_ZONE).
app.conf.beat_schedule = {
    "sync-kobo-daily": {
        "task": "apps.kobo.tasks.sync_kobo",
        "schedule": crontab(minute=0, hour=0),  # 00:00 UTC == 03:00 EAT daily
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.info("Request: %s", self.request)


@signals.setup_logging.connect
def config_loggers(**_):
    from django.conf import settings  # noqa: PLC0415

    dictConfig(settings.LOGGING)
