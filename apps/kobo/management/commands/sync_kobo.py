"""Fetch ERCS EOC Kobo submissions on demand and reconcile them into the store.

Usage
-----
    ./manage.py sync_kobo                 # sync all three forms
    ./manage.py sync_kobo --dry-run       # fetch + log, but roll back DB writes
    ./manage.py sync_kobo --form alert     # sync a single form (alert|rna|field)

This is the same reconcile the daily Celery beat runs (``apps.kobo.tasks.sync_kobo``);
it is a full mirror, so it is safe to run any time and a missed run self-heals.
"""

import typing
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from apps.kobo.models import KoboForm
from apps.kobo.sync import KoboSyncer

_FORM_CHOICES: dict[str, KoboForm] = {
    "alert": KoboForm.EMERGENCY_ALERT,
    "rna": KoboForm.RAPID_NEEDS_ASSESSMENT,
    "field": KoboForm.EMERGENCY_FIELD,
}


class Command(BaseCommand):
    help = "Fetch ERCS EOC Kobo submissions and reconcile them into the local store."

    @typing.override
    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Fetch and log what would change, but roll back all DB writes.",
        )
        parser.add_argument(
            "--form",
            choices=sorted(_FORM_CHOICES),
            help="Sync only a single form (default: all three).",
        )

    @typing.override
    def handle(self, *args: Any, **options: Any) -> None:
        dry_run: bool = options["dry_run"]
        only = _FORM_CHOICES[options["form"]] if options.get("form") else None

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run mode — changes will be rolled back."))

        syncer = KoboSyncer(stdout=self.stdout, style=self.style)
        results = syncer.run(dry_run=dry_run, only=only)

        failed = [r for r in results if not r.ok]
        self.stdout.write(self.style.SUCCESS(f"\nSync complete: {len(results) - len(failed)}/{len(results)} forms OK."))
        if failed:
            names = ", ".join(KoboForm(r.form).label for r in failed)
            raise CommandError(f"{len(failed)} form(s) failed: {names}")
