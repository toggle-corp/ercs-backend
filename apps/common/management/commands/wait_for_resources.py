import signal
import time
import typing

from django.core.management.base import BaseCommand, CommandParser
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Wait for resources the application depends on before starting"

    def wait_for_db(self) -> None:
        self.stdout.write("Waiting for DB...")
        start_time = time.time()
        while True:
            try:
                db_conn = connections["default"]
                db_conn.ensure_connection()
                break
            except OperationalError:
                pass
            self.stdout.write(self.style.WARNING("DB not available, waiting 1s..."))
            time.sleep(1)
        self.stdout.write(
            self.style.SUCCESS(f"DB available after {time.time() - start_time:.1f}s")
        )

    @typing.override
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--timeout",
            type=int,
            default=600,
            help="Max seconds to wait before giving up (default: 600).",
        )
        parser.add_argument("--db", action="store_true", help="Wait for the database")
        parser.add_argument("--all", action="store_true", help="Wait for all resources")

    @typing.override
    def handle(self, **kwargs: typing.Any) -> None:
        timeout = kwargs["timeout"]
        _all = kwargs["all"]

        def _timeout_handler(*_: typing.Any) -> None:
            raise TimeoutError("wait_for_resources timed out.")

        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(timeout)

        try:
            if _all or kwargs["db"]:
                self.wait_for_db()
        finally:
            signal.alarm(0)
