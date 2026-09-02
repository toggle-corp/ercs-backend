import datetime
import typing

from apps.kobo.factories import KoboSubmissionFactory
from apps.kobo.models import KoboForm, KoboSyncState
from main.tests import TestCase


class TestKoboStatsQuery(TestCase):
    class Query:
        KOBO_STATS = """
            query KoboStats {
                koboStats {
                    generatedAt
                    alert {
                        source { form formLabel assetUid lastFetchedAt confirmedRecords }
                        totalEmergencies
                        peopleAffected
                        peopleDisplaced
                        byHazard { key count }
                        byRegion { key count }
                    }
                    rapidNeeds { totalAssessments peopleInNeed }
                    field { totalReports peopleReached }
                }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Two confirmed alerts (distinct emergencies) + one unapproved (excluded).
        KoboSubmissionFactory.create(
            form=KoboForm.EMERGENCY_ALERT,
            emergency_code="EM-A",
            raw={
                "context/hazard": "flood",
                "geo/region-one": "Oromia",
                "ppl_impact_group/ppl_affected": "1000",
                "ppl_impact_group/ppl_affected_displaced": "100",
                "emergency_code/unique_code": "EM-A",
            },
        )
        KoboSubmissionFactory.create(
            form=KoboForm.EMERGENCY_ALERT,
            emergency_code="EM-B",
            raw={
                "context/hazard": "flood",
                "geo/region-one": "Tigray",
                "ppl_impact_group/ppl_affected": "500",
                "ppl_impact_group/ppl_affected_displaced": "50",
                "emergency_code/unique_code": "EM-B",
            },
        )
        KoboSubmissionFactory.create(
            form=KoboForm.EMERGENCY_ALERT,
            validation_status="validation_status_not_approved",
            emergency_code="EM-C",
            raw={"ppl_impact_group/ppl_affected": "9999", "emergency_code/unique_code": "EM-C"},
        )
        KoboSyncState.objects.create(
            form=KoboForm.EMERGENCY_ALERT,
            asset_uid="aydYC8AYCDuX7y4PwfvgrX",
            last_fetched_at=datetime.datetime(2026, 8, 27, tzinfo=datetime.UTC),
            last_status=KoboSyncState.Status.SUCCESS,
            record_count=3,
        )

    def test_kobo_stats(self):
        content = self.query_check(self.Query.KOBO_STATS)
        alert = content["data"]["koboStats"]["alert"]

        # Only the two approved submissions are counted.
        assert alert["totalEmergencies"] == 2
        assert alert["peopleAffected"] == 1500
        assert alert["peopleDisplaced"] == 150
        assert alert["source"]["confirmedRecords"] == 2
        assert alert["source"]["lastFetchedAt"] is not None
        assert {b["key"]: b["count"] for b in alert["byHazard"]} == {"flood": 2}
        assert {b["key"]: b["count"] for b in alert["byRegion"]} == {"Oromia": 1, "Tigray": 1}


class TestFieldReachedDedup(TestCase):
    """People Reached must be max per (emergency_code, branch), not a naive sum,
    because `g_reach` is reported per period and would double-count.
    """

    def _make(self, code: str, branch: str, reach: int):
        KoboSubmissionFactory.create(
            form=KoboForm.EMERGENCY_FIELD,
            asset_uid="aby6sxp4DyEiohs4XMn7Mu",
            emergency_code=code,
            raw={
                "location/alert_code": code,
                "context/reporting_branch": branch,
                "branch_sitrep/reached_population/g_reach": str(reach),
            },
        )

    def test_people_reached_is_max_per_branch(self):
        from apps.kobo.stats import build_kobo_stats

        # Same (code, branch) reported twice -> only the max (300) should count.
        self._make("EM-1", "B1", 100)
        self._make("EM-1", "B1", 300)
        # Different branch, same emergency -> additive.
        self._make("EM-1", "B2", 50)
        # Different emergency, same branch -> additive.
        self._make("EM-2", "B1", 200)

        stats = build_kobo_stats()
        # max(100,300) + 50 + 200 = 550  (naive sum would be 650)
        assert stats.field.people_reached == 550
        assert stats.field.total_reports == 4

    def test_unkeyed_rows_are_not_collapsed(self):
        """Rows with neither emergency code nor branch each stand on their own.

        Sharing one ``(None, None)`` bucket would let ``max()`` throw all but the
        largest away.
        """
        from apps.kobo.stats import build_kobo_stats

        for reach in (100, 200):
            KoboSubmissionFactory.create(
                form=KoboForm.EMERGENCY_FIELD,
                asset_uid="aby6sxp4DyEiohs4XMn7Mu",
                emergency_code=None,
                raw={"branch_sitrep/reached_population/g_reach": str(reach)},
            )

        assert build_kobo_stats().field.people_reached == 300


class TestFieldResourceDedup(TestCase):
    """Mobilized resources are restated in every periodic sitrep, so they get the
    same per-(emergency, branch) treatment as People Reached.
    """

    def _make(self, code: str, branch: str, **raw: str):
        KoboSubmissionFactory.create(
            form=KoboForm.EMERGENCY_FIELD,
            asset_uid="aby6sxp4DyEiohs4XMn7Mu",
            emergency_code=code,
            raw={"context/reporting_branch": branch, **raw},
        )

    def test_resources_are_not_summed_across_periods(self):
        from apps.kobo.stats import build_kobo_stats

        # One branch, two reporting periods, the same standing figures.
        for _ in range(2):
            self._make(
                "EM-1",
                "B1",
                **{
                    "branch_sitrep/resources_group/resources_staff": "8",
                    "branch_sitrep/resources_group/resources_volunteers": "3",
                    "branch_sitrep/resources_group/resources_BDRT": "7",
                },
            )
        # A second branch is additive.
        self._make("EM-1", "B2", **{"branch_sitrep/resources_group/resources_staff": "2"})

        stats = build_kobo_stats()
        assert stats.field.staff_mobilized == 10  # 8 + 2, not 8 + 8 + 2
        assert stats.field.volunteers_mobilized == 3
        assert stats.field.bdrt_mobilized == 7

    def test_support_requested_reads_support_required(self):
        """``support_required`` is a select_multiple, not a yes/no."""
        from apps.kobo.stats import build_kobo_stats

        # Same branch asks in both of its sitreps -> counted once.
        for _ in range(2):
            self._make("EM-1", "B1", **{"branch_sitrep/resources_group/support_required": "relief_nfi coordination"})
        self._make("EM-1", "B2", **{"branch_sitrep/resources_group/support_required": "allocation_funds_response"})
        # Nothing requested.
        self._make("EM-2", "B3", **{"branch_sitrep/resources_group/support_required": ""})

        assert build_kobo_stats().field.support_requested == 2
