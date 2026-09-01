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
