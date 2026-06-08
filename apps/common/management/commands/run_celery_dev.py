import shlex
import subprocess
import typing
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import autoreload

WORKER_STATE_DIR = Path("/var/run/celery")

CMD = "celery -A main worker -E --concurrency=2 -l info"


def restart_celery(*args: typing.Any, **kwargs: typing.Any) -> None:
    subprocess.call(shlex.split("pkill -9 celery"))
    subprocess.call(shlex.split(CMD))


class Command(BaseCommand):
    """Start a Celery worker with Django's autoreloader so it restarts on code changes."""

    @typing.override
    def handle(self, *args: typing.Any, **options: typing.Any) -> None:
        self.stdout.write("Starting celery worker with autoreload...")
        WORKER_STATE_DIR.mkdir(parents=True, exist_ok=True)
        autoreload.run_with_reloader(restart_celery)
