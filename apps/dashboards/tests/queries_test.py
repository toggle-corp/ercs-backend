import typing

from apps.dashboards.factories import ExternalDashboardFactory
from apps.dashboards.models import ExternalDashboard
from apps.users.factories import UserFactory
from main.tests import TestCase


class TestExternalDashboardQueries(TestCase):
    class Query:
        DASHBOARDS = """
            query ExternalDashboards($pagination: OffsetPaginationInput, $filters: ExternalDashboardFilter) {
                externalDashboards(pagination: $pagination, filters: $filters, order: {page: ASC}) {
                    totalCount
                    pageInfo { offset limit }
                    results {
                        id
                        title
                        url
                        page
                        isActive
                        showOnHome
                        order
                        createdAt
                    }
                }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.home_db = ExternalDashboardFactory.create(page=ExternalDashboard.Page.HOME, order=0)
        cls.ops_db = ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=0)
        cls.inactive = ExternalDashboardFactory.create(is_active=False, page=ExternalDashboard.Page.OPERATIONS)

    def test_all_dashboards(self):
        content = self.query_check(
            self.Query.DASHBOARDS,
            variables={"pagination": {"limit": 10, "offset": 0}},
        )
        assert content["data"]["externalDashboards"]["totalCount"] == 3

    def test_filter_active(self):
        content = self.query_check(
            self.Query.DASHBOARDS,
            variables={
                "pagination": {"limit": 10, "offset": 0},
                "filters": {"isActive": True},
            },
        )
        assert content["data"]["externalDashboards"]["totalCount"] == 2

    def test_filter_by_page(self):
        content = self.query_check(
            self.Query.DASHBOARDS,
            variables={
                "pagination": {"limit": 10, "offset": 0},
                "filters": {"page": str(ExternalDashboard.Page.HOME)},
            },
        )
        results = content["data"]["externalDashboards"]["results"]
        assert len(results) == 1
        assert results[0]["page"] == ExternalDashboard.Page.HOME
