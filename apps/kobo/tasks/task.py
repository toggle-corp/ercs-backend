import logging

from celery import shared_task

from apps.kobo.sync import KoboSyncer

logger = logging.getLogger(__name__)


@shared_task(name="apps.kobo.tasks.sync_kobo")
def sync_kobo() -> dict[str, bool]:
    """Delegates to the same :class:`KoboSyncer` as the ``sync_kobo`` management
    command. Per-form isolation lives inside the syncer, so one form failing
    does not abort the others.
    """
    results = KoboSyncer().run()
    summary = {r.form.name: r.ok for r in results}
    logger.info("sync_kobo task finished: %s", summary)
    return summary
