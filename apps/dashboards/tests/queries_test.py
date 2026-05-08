# apps/dashboards/tests/test_queries.py
import typing

from apps.dashboards.factories import CapacityAndResourceFactory, ExternalDashboardFactory
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


class TestCapacityAndResourceQueries(TestCase):
    class Query:
        CAPACITY_AND_RESOURCES = """
            query CapacityAndResources($pagination: OffsetPaginationInput, $filters: CapacityAndResourceFilter) {
                capacityAndResources(pagination: $pagination, filters: $filters, order: {order: ASC}) {
                    totalCount
                    pageInfo { offset limit }
                    results {
                        id
                        title
                        description
                        isActive
                        order
                        createdAt
                        dashboards {
                                id
                                title
                                url
                                page
                            }
                        }
                    }
                }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()

        cls.dashboard_1 = ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.CAPACITY_RESOURCES,
            order=0,
        )
        cls.dashboard_2 = ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.CAPACITY_RESOURCES,
            order=1,
        )

        cls.capacity_1 = CapacityAndResourceFactory.create(order=0, is_active=True)
        cls.capacity_1.dashboards.set([cls.dashboard_1])
        cls.capacity_2 = CapacityAndResourceFactory.create(order=1, is_active=True)
        cls.capacity_2.dashboards.set([cls.dashboard_2])
        cls.capacity_inactive = CapacityAndResourceFactory.create(order=2, is_active=False)
        cls.capacity_inactive.dashboards.set([cls.dashboard_1])

    def test_all_capacity_and_resources(self):
        content = self.query_check(
            self.Query.CAPACITY_AND_RESOURCES,
            variables={"pagination": {"limit": 10, "offset": 0}},
        )
        assert content["data"]["capacityAndResources"]["totalCount"] == 3

    def test_filter_active(self):
        content = self.query_check(
            self.Query.CAPACITY_AND_RESOURCES,
            variables={
                "pagination": {"limit": 10, "offset": 0},
                "filters": {"isActive": True},
            },
        )
        assert content["data"]["capacityAndResources"]["totalCount"] == 2

    def test_search(self):
        content = self.query_check(
            self.Query.CAPACITY_AND_RESOURCES,
            variables={
                "pagination": {"limit": 10, "offset": 0},
                "filters": {"search": self.capacity_1.title},
            },
        )
        results = content["data"]["capacityAndResources"]["results"]
        assert len(results) == 1
        assert results[0]["title"] == self.capacity_1.title

    def test_pagination(self):
        content = self.query_check(
            self.Query.CAPACITY_AND_RESOURCES,
            variables={"pagination": {"limit": 2, "offset": 0}},
        )
        assert len(content["data"]["capacityAndResources"]["results"]) == 2
        assert content["data"]["capacityAndResources"]["totalCount"] == 3
