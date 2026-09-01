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
from typing import Any

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

# A confirmed submission, as loaded for aggregation: (raw_record, matched_region_name).
Row = tuple[dict[str, Any], str | None]


def _to_int(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _humanize(value: str) -> str:
    return value.replace("_", " ").strip()


def _sum(rows: list[Row], key: str) -> int:
    return sum(_to_int(raw.get(key)) for raw, _ in rows)


def _breakdown(rows: list[Row], key: str) -> list[KeyCount]:
    counter = Counter(str(raw.get(key)) for raw, _ in rows if raw.get(key))
    return [KeyCount(key=k, count=n) for k, n in counter.most_common()]


def _region_breakdown(rows: list[Row], raw_key: str) -> list[KeyCount]:
    """Count by matched AdminArea name, falling back to the humanized raw name."""
    counter: Counter[str] = Counter()
    for raw, region_name in rows:
        name = region_name or _humanize(str(raw.get(raw_key) or "")) or "Unknown"
        counter[name] += 1
    return [KeyCount(key=k, count=n) for k, n in counter.most_common()]


def _source(form: KoboForm, confirmed: int) -> KoboSource:
    state = KoboSyncState.objects.filter(form=form).first()
    return KoboSource(
        form=int(form),
        form_label=KoboForm(form).label,
        asset_uid=state.asset_uid if state else "",
        last_fetched_at=state.last_fetched_at if state else None,
        last_status=state.last_status if state else "",
        total_records=state.record_count if state else 0,
        confirmed_records=confirmed,
    )


def _confirmed(form: KoboForm) -> list[Row]:
    return list(
        KoboSubmission.objects.filter(
            form=form,
            validation_status=VALIDATION_STATUS_APPROVED,
        ).values_list("raw", "region__name"),
    )


def _alert_stats() -> AlertStats:
    rows = _confirmed(KoboForm.EMERGENCY_ALERT)
    codes = {raw.get("emergency_code/unique_code") for raw, _ in rows if raw.get("emergency_code/unique_code")}
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


def _field_reached(rows: list[Row]) -> int:
    """De-duplicated people reached.

    ``g_reach`` is reported *per reporting period*, so summing across a branch's
    periodic sitreps double-counts recurring beneficiaries. We take the maximum
    reached per ``(emergency_code, reporting_branch)`` as a proxy for that
    branch's response, then sum across branches/emergencies.
    """
    max_by_branch: dict[tuple[str | None, str | None], int] = {}
    for raw, _ in rows:
        key = (
            raw.get("location/alert_code") or raw.get("context/emergency-selection"),
            raw.get("context/reporting_branch"),
        )
        max_by_branch[key] = max(
            max_by_branch.get(key, 0),
            _to_int(raw.get("branch_sitrep/reached_population/g_reach")),
        )
    return sum(max_by_branch.values())


def _field_stats() -> FieldStats:
    rows = _confirmed(KoboForm.EMERGENCY_FIELD)
    support = sum(1 for raw, _ in rows if raw.get("branch_sitrep/resources_group/support_request") == "yes")
    return FieldStats(
        source=_source(KoboForm.EMERGENCY_FIELD, len(rows)),
        total_reports=len(rows),
        people_reached=_field_reached(rows),
        staff_mobilized=_sum(rows, "branch_sitrep/resources_group/resources_staff"),
        volunteers_mobilized=_sum(rows, "branch_sitrep/resources_group/resources_volunteers"),
        bdrt_mobilized=_sum(rows, "branch_sitrep/resources_group/resources_BDRT"),
        ambulances_mobilized=_sum(rows, "branch_sitrep/resources_group/resources_ambulances"),
        support_requested=support,
        by_region=_region_breakdown(rows, "location/region-one"),
    )


def build_kobo_stats() -> KoboStats:
    return KoboStats(
        generated_at=timezone.now(),
        alert=_alert_stats(),
        rapid_needs=_rapid_needs_stats(),
        field=_field_stats(),
    )
