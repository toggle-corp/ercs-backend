import strawberry
import strawberry_django

from apps.kobo.models import KoboSubmission


@strawberry_django.order_type(KoboSubmission)
class KoboSubmissionOrder:
    submission_time: strawberry.auto
    kobo_id: strawberry.auto
