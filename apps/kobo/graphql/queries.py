import strawberry
import strawberry_django
from asgiref.sync import sync_to_async
from strawberry_django.pagination import OffsetPaginated

from apps.kobo.stats import build_kobo_stats

from .filters import KoboSubmissionFilter
from .orders import KoboSubmissionOrder
from .types import KoboStats, KoboSubmissionType


@strawberry.type
class Query:
    # Key stats for the public dashboards, each carrying its source (form + asset
    # uid) and last-fetched date. Public, like the other dashboard queries.
    @strawberry.field
    @sync_to_async
    def kobo_stats(self) -> KoboStats:
        return build_kobo_stats()

    kobo_submissions: OffsetPaginated[KoboSubmissionType] = strawberry_django.offset_paginated(
        filters=KoboSubmissionFilter,
        order=KoboSubmissionOrder,
    )

    kobo_submission: KoboSubmissionType = strawberry_django.field()
