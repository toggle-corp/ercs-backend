"""Compute the key dashboard stats from stored (confirmed) Kobo submissions.

Numbers live as strings inside ``raw`` (Kobo exports everything as text), so
aggregation happens in Python. Volumes are small (hundreds of rows/form), so a
single pass per form is more than fast enough. Only submissions whose
``validation_status`` is approved are counted.

Region breakdowns use the ``AdminArea`` matched during sync (a clean canonical
name like "Oromia"); if a submission's region did not match, we fall back to a
humanized version of the raw Kobo region string (e.g. ``South_Ethiopia`` →
``South Ethiopia``).
"""

from collections import Counter
from typing import Any, NamedTuple

from django.utils import timezone

from apps.kobo.graphql.types import (
    AlertStats,
    FieldStats,
    KeyCount,
    KoboSource,
    KoboStats,
    RapidNeedsStats,
)
from apps.kobo.models import VALIDATION_STATUS_APPROVED, KoboForm, KoboSubmission, KoboSyncState


class Row(NamedTuple):
    """A confirmed submission, as loaded for aggregation."""

    raw: dict[str, Any]
    region_name: str | None
    emergency_code: str | None
    kobo_id: int


def _to_int(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _humanize(value: str) -> str:
    return value.replace("_", " ").strip()


def _sum(rows: list[Row], key: str) -> int:
    return sum(_to_int(row.raw.get(key)) for row in rows)


def _breakdown(rows: list[Row], key: str) -> list[KeyCount]:
    counter = Counter(str(row.raw.get(key)) for row in rows if row.raw.get(key))
    return [KeyCount(key=k, count=n) for k, n in counter.most_common()]


def _region_breakdown(rows: list[Row], raw_key: str) -> list[KeyCount]:
    """Count by matched AdminArea name, falling back to the humanized raw name."""
    counter: Counter[str] = Counter()
    for row in rows:
        name = row.region_name or _humanize(str(row.raw.get(raw_key) or "")) or "Unknown"
        counter[name] += 1
    return [KeyCount(key=k, count=n) for k, n in counter.most_common()]


def _source(form: KoboForm, confirmed: int) -> KoboSource:
    state = KoboSyncState.objects.filter(form=form).first()
    return KoboSource(
        form=int(form),
        form_label=str(KoboForm(form).label),
        asset_uid=state.asset_uid if state else "",
        last_fetched_at=state.last_fetched_at if state else None,
        last_status=state.last_status if state else "",
        total_records=state.record_count if state else 0,
        confirmed_records=confirmed,
    )


def _confirmed(form: KoboForm) -> list[Row]:
    return [
        Row(*values)
        for values in KoboSubmission.objects.filter(
            form=form,
            validation_status=VALIDATION_STATUS_APPROVED,
        ).values_list("raw", "region__name", "emergency_code", "kobo_id")
    ]


def _alert_stats() -> AlertStats:
    rows = _confirmed(KoboForm.EMERGENCY_ALERT)
    # The promoted column, derived once during sync from `FORM_SPECS`.
    codes = {row.emergency_code for row in rows if row.emergency_code}
    return AlertStats(
        source=_source(KoboForm.EMERGENCY_ALERT, len(rows)),
        total_emergencies=len(codes),
        people_affected=_sum(rows, "ppl_impact_group/ppl_affected"),
        people_displaced=_sum(rows, "ppl_impact_group/ppl_affected_displaced"),
        deaths=_sum(rows, "ppl_impact_group/ppl_dead"),
        injured=_sum(rows, "ppl_impact_group/ppl_wounded"),
        missing=_sum(rows, "ppl_impact_group/ppl_missing"),
        by_hazard=_breakdown(rows, "context/hazard"),
        by_region=_region_breakdown(rows, "geo/region-one"),
    )


def _rapid_needs_stats() -> RapidNeedsStats:
    rows = _confirmed(KoboForm.RAPID_NEEDS_ASSESSMENT)
    return RapidNeedsStats(
        source=_source(KoboForm.RAPID_NEEDS_ASSESSMENT, len(rows)),
        total_assessments=len(rows),
        people_in_need=_sum(rows, "ppl_impact_group/ppl_in_need"),
        people_affected=_sum(rows, "ppl_impact_group/ppl_affected"),
        people_displaced=_sum(rows, "ppl_impact_group/ppl_affected_displaced"),
        top_priority_sectors=_breakdown(rows, "priority_sectors/sector1"),
        by_region=_region_breakdown(rows, "location/region"),
    )


def _branch_key(row: Row) -> tuple[Any, Any]:
    """The ``(emergency, branch)`` bucket a Field sitrep belongs to.

    A row with neither key becomes its own bucket, keyed on ``kobo_id`` —
    collapsing every unkeyed row into one shared bucket would let
    :func:`_max_per_branch` discard all but the largest of them.
    """
    branch = row.raw.get("context/reporting_branch")
    if not row.emergency_code and not branch:
        return ("kobo_id", row.kobo_id)
    return (row.emergency_code, branch)


def _max_per_branch(rows: list[Row], key: str) -> int:
    """Sum ``key``'s peak value per ``(emergency, branch)``.

    Field figures are restated in every periodic sitrep, so a plain sum
    multiplies a branch's contribution by how often it reported. We take that
    branch's peak for the emergency as the proxy for its response, then sum
    across branches and emergencies.
    """
    peaks: dict[tuple[Any, Any], int] = {}
    for row in rows:
        bucket = _branch_key(row)
        peaks[bucket] = max(peaks.get(bucket, 0), _to_int(row.raw.get(key)))
    return sum(peaks.values())


def _support_requested(rows: list[Row]) -> int:
    """Branch responses that requested support at least once.

    ``support_required`` is a ``select_multiple``: a space-delimited list of what
    the branch needs, absent/empty when nothing was requested. Counted per
    ``(emergency, branch)`` like the other Field figures, so a branch repeating
    the request in each sitrep still counts once.
    """
    return len({_branch_key(row) for row in rows if row.raw.get("branch_sitrep/resources_group/support_required")})


def _field_stats() -> FieldStats:
    rows = _confirmed(KoboForm.EMERGENCY_FIELD)
    return FieldStats(
        source=_source(KoboForm.EMERGENCY_FIELD, len(rows)),
        total_reports=len(rows),
        people_reached=_max_per_branch(rows, "branch_sitrep/reached_population/g_reach"),
        staff_mobilized=_max_per_branch(rows, "branch_sitrep/resources_group/resources_staff"),
        volunteers_mobilized=_max_per_branch(rows, "branch_sitrep/resources_group/resources_volunteers"),
        bdrt_mobilized=_max_per_branch(rows, "branch_sitrep/resources_group/resources_BDRT"),
        ambulances_mobilized=_max_per_branch(rows, "branch_sitrep/resources_group/resources_ambulances"),
        support_requested=_support_requested(rows),
        by_region=_region_breakdown(rows, "location/region-one"),
    )


def build_kobo_stats() -> KoboStats:
    return KoboStats(
        generated_at=timezone.now(),
        alert=_alert_stats(),
        rapid_needs=_rapid_needs_stats(),
        field=_field_stats(),
    )
