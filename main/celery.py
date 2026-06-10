import logging
import os
from logging.config import dictConfig

from celery import Celery, signals

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

app = Celery("main")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.task_default_queue = "default"

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.info("Request: %s", self.request)


@signals.setup_logging.connect
def config_loggers(**_):
    from django.conf import settings  # noqa: PLC0415

    dictConfig(settings.LOGGING)
