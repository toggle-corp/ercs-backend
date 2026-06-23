# apps/dashboards/tests/test_mutations.py
import typing

from apps.dashboards.factories import CapacityAndResourceFactory, ExternalDashboardFactory
from apps.dashboards.models import CapacityAndResource, ExternalDashboard
from apps.dashboards.serializers import ExternalDashboardSerializer
from apps.users.factories import UserFactory
from apps.users.models import User
from main.tests import TestCase


class TestExternalDashboardMutations(TestCase):
    class Mutation:
        ADD_TO_HOME = """
            mutation AddDashboardToHome($id: ID!) {
                addDashboardToHome(id: $id) {
                    ... on ExternalDashboardTypeMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            showOnHome
                        }
                    }
                }
            }
        """

        REMOVE_FROM_HOME = """
            mutation RemoveDashboardFromHome($id: ID!) {
                removeDashboardFromHome(id: $id) {
                    ... on ExternalDashboardTypeMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            showOnHome
                        }
                    }
                }
            }
        """

        CREATE_DASHBOARD = """
            mutation CreateExternalDashboard($data: ExternalDashboardCreateInput!) {
                createExternalDashboard(data: $data) {
                    ... on ExternalDashboardTypeMutationResponseType{
                    ok
                    errors
                    result {
                        id
                        title
                        url
                        page
                        isActive
                        showOnHome
                    }
                }
            }
        }
        """

        UPDATE_DASHBOARD = """
            mutation UpdateExternalDashboard($id: ID!, $data: ExternalDashboardUpdateInput!) {
                updateExternalDashboard(id: $id, data: $data) {
                    ... on ExternalDashboardTypeMutationResponseType{
                    ok
                    errors
                    result {
                        id
                        title
                        isActive
                    }
                }
            }
        }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff = UserFactory.create(role=User.Role.STAFF)
        cls.viewer = UserFactory.create(role=User.Role.VIEWER)

    def test_create_dashboard(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.CREATE_DASHBOARD,
            variables={
                "data": {
                    "title": "Operations KPIs",
                    "url": "https://app.powerbi.com/embed/ops",
                    "page": ExternalDashboard.Page.OPERATIONS.name,
                },
            },
        )
        resp = content["data"]["createExternalDashboard"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "Operations KPIs"
        assert resp["result"]["page"] == ExternalDashboard.Page.OPERATIONS.name

    def test_viewer_cannot_create(self):
        self.force_login(self.viewer)
        content = self.query_check(
            self.Mutation.CREATE_DASHBOARD,
            assert_errors=True,
            variables={
                "data": {
                    "title": "Blocked",
                    "url": "https://example.com",
                    "page": ExternalDashboard.Page.HOME.name,
                },
            },
        )
        assert "errors" in content

    def test_deactivate_dashboard(self):
        self.force_login(self.staff)
        db = ExternalDashboardFactory.create(is_active=True, created_by=self.staff)
        content = self.query_check(
            self.Mutation.UPDATE_DASHBOARD,
            variables={"id": str(db.pk), "data": {"isActive": False}},
        )
        resp = content["data"]["updateExternalDashboard"]
        assert resp["ok"] is True
        assert resp["result"]["isActive"] is False

    def test_add_dashboard_to_home(self):
        self.force_login(self.staff)
        dashboard = ExternalDashboardFactory.create(show_on_home=False)
        content = self.query_check(
            self.Mutation.ADD_TO_HOME,
            variables={"id": str(dashboard.pk)},
        )
        resp = content["data"]["addDashboardToHome"]
        assert resp["ok"] is True
        assert resp["result"]["showOnHome"] is True
        dashboard.refresh_from_db()
        assert dashboard.show_on_home is True

    def test_add_dashboard_to_home_idempotent(self):
        self.force_login(self.staff)
        dashboard = ExternalDashboardFactory.create(show_on_home=True)
        content = self.query_check(
            self.Mutation.ADD_TO_HOME,
            variables={"id": str(dashboard.pk)},
        )
        resp = content["data"]["addDashboardToHome"]
        assert resp["ok"] is True
        assert resp["result"]["showOnHome"] is True

    def test_add_dashboard_to_home_limit_exceeded(self):
        self.force_login(self.staff)
        for _ in range(ExternalDashboardSerializer.HOME_DASHBOARD_LIMIT):
            ExternalDashboardFactory.create(show_on_home=True)
        dashboard = ExternalDashboardFactory.create(show_on_home=False)
        content = self.query_check(
            self.Mutation.ADD_TO_HOME,
            variables={"id": str(dashboard.pk)},
        )
        resp = content["data"]["addDashboardToHome"]
        assert resp["ok"] is False
        assert resp["errors"] is not None
        dashboard.refresh_from_db()
        assert dashboard.show_on_home is False

    def test_viewer_cannot_add_to_home(self):
        self.force_login(self.viewer)
        dashboard = ExternalDashboardFactory.create(show_on_home=False)
        content = self.query_check(
            self.Mutation.ADD_TO_HOME,
            assert_errors=True,
            variables={"id": str(dashboard.pk)},
        )
        assert "errors" in content

    def test_remove_dashboard_from_home(self):
        self.force_login(self.staff)
        dashboard = ExternalDashboardFactory.create(show_on_home=True)
        content = self.query_check(
            self.Mutation.REMOVE_FROM_HOME,
            variables={"id": str(dashboard.pk)},
        )
        resp = content["data"]["removeDashboardFromHome"]
        assert resp["ok"] is True
        assert resp["result"]["showOnHome"] is False
        dashboard.refresh_from_db()
        assert dashboard.show_on_home is False

    def test_viewer_cannot_remove_from_home(self):
        self.force_login(self.viewer)
        dashboard = ExternalDashboardFactory.create(show_on_home=True)
        content = self.query_check(
            self.Mutation.REMOVE_FROM_HOME,
            assert_errors=True,
            variables={"id": str(dashboard.pk)},
        )
        assert "errors" in content


class TestCapacityAndResourceMutations(TestCase):
    class Mutation:
        CREATE_CAPACITY_AND_RESOURCE = """
            mutation CreateCapacityAndResource($data: CapacityAndResourceCreateInput!) {
                createCapacityAndResource(data: $data) {
                    ... on CapacityAndResourceTypeMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            title
                            description
                            isActive
                            order
                            dashboards {
                                id
                                title
                                page
                            }
                        }
                    }
                }
            }
        """

        UPDATE_CAPACITY_AND_RESOURCE = """
            mutation UpdateCapacityAndResource($id: ID!, $data: CapacityAndResourceUpdateInput!) {
                updateCapacityAndResource(id: $id, data: $data) {
                    ... on CapacityAndResourceTypeMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            title
                            isActive
                            dashboards {
                                id
                                title
                            }
                        }
                    }
                }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(self):
        super().setUpClass()

        self.staff = UserFactory.create(role=User.Role.STAFF)
        self.viewer = UserFactory.create(role=User.Role.VIEWER)

        self.dashboard_1 = ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.CAPACITY_RESOURCES,
            order=1,
        )

        self.dashboard_2 = ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.CAPACITY_RESOURCES,
            order=2,
        )

    def test_create_capacity_and_resource(self):
        self.force_login(self.staff)

        content = self.query_check(
            self.Mutation.CREATE_CAPACITY_AND_RESOURCE,
            variables={
                "data": {
                    "title": "Water & Sanitation",
                    "description": "WASH capacity overview",
                    "isActive": True,
                    "order": 1,
                    "dashboards": [
                        self.dashboard_1.pk,
                        self.dashboard_2.pk,
                    ],
                },
            },
        )
        resp = content["data"]["createCapacityAndResource"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "Water & Sanitation"
        instance = CapacityAndResource.objects.get(title="Water & Sanitation")
        assert instance.dashboards.count() == 2
        assert not instance.dashboards.exclude(
            page=ExternalDashboard.Page.CAPACITY_RESOURCES,
        ).exists()

    def test_create_resource_with_non_capacity_type_dashboard(self):
        self.force_login(self.staff)
        dashboard = ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.EMERGENCY_ALERTS,
            order=111,
        )

        content = self.query_check(
            self.Mutation.CREATE_CAPACITY_AND_RESOURCE,
            variables={
                "data": {
                    "title": "Empty Capacity",
                    "isActive": True,
                    "order": 1,
                    "dashboards": [dashboard.pk],
                },
            },
        )

        resp = content["data"]["createCapacityAndResource"]

        assert resp["ok"] is False
        assert resp["errors"] is not None

    def test_viewer_cannot_create(self):
        self.force_login(self.viewer)

        content = self.query_check(
            self.Mutation.CREATE_CAPACITY_AND_RESOURCE,
            assert_errors=True,
            variables={
                "data": {
                    "title": "Blocked",
                    "isActive": True,
                    "order": 0,
                },
            },
        )

        assert "errors" in content

    def test_deactivate_capacity_and_resource(self):
        self.force_login(self.staff)

        instance = CapacityAndResourceFactory.create(
            is_active=True,
        )

        instance.dashboards.set([self.dashboard_1])

        content = self.query_check(
            self.Mutation.UPDATE_CAPACITY_AND_RESOURCE,
            variables={
                "id": instance.pk,
                "data": {
                    "isActive": False,
                },
            },
        )

        resp = content["data"]["updateCapacityAndResource"]

        assert resp["ok"] is True
        assert resp["result"]["isActive"] is False

    def test_update_capacity_and_resource(self):
        self.force_login(self.staff)

        capacity_and_resource = CapacityAndResourceFactory.create(
            is_active=True,
            order=1,
        )
        capacity_and_resource.dashboards.set([self.dashboard_1])
        content = self.query_check(
            self.Mutation.UPDATE_CAPACITY_AND_RESOURCE,
            variables={
                "id": str(capacity_and_resource.pk),
                "data": {
                    "title": "Updated Title",
                    "isActive": False,
                    "dashboards": [self.dashboard_2.pk],
                },
            },
        )

        resp = content["data"]["updateCapacityAndResource"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "Updated Title"
        assert resp["result"]["isActive"] is False

        capacity_and_resource.refresh_from_db()
        assert capacity_and_resource.dashboards.count() == 1
        assert not capacity_and_resource.dashboards.filter(pk=self.dashboard_1.pk).exists()
        assert capacity_and_resource.dashboards.filter(pk=self.dashboard_2.pk).exists()

    def test_update_without_dashboards_keeps_existing(self):
        self.force_login(self.staff)

        capacity_and_resource = CapacityAndResourceFactory.create(is_active=True, order=1)
        capacity_and_resource.dashboards.set([self.dashboard_1, self.dashboard_2])

        content = self.query_check(
            self.Mutation.UPDATE_CAPACITY_AND_RESOURCE,
            variables={
                "id": capacity_and_resource.pk,
                "data": {
                    "title": "No Dashboard Change",
                },
            },
        )

        resp = content["data"]["updateCapacityAndResource"]
        assert resp["ok"] is True

        capacity_and_resource.refresh_from_db()
        assert capacity_and_resource.dashboards.count() == 2

    def test_update_with_invalid_dashboard_page(self):
        self.force_login(self.staff)

        capacity_and_resource = CapacityAndResourceFactory.create(is_active=True, order=1)
        capacity_and_resource.dashboards.set([self.dashboard_1])
        invalid_dashboard = ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.EMERGENCY_ALERTS,
            order=999,
        )

        content = self.query_check(
            self.Mutation.UPDATE_CAPACITY_AND_RESOURCE,
            variables={
                "id": capacity_and_resource.pk,
                "data": {
                    "dashboards": [invalid_dashboard.pk],
                },
            },
        )
        resp = content["data"]["updateCapacityAndResource"]
        assert resp["ok"] is False
        assert resp["errors"] is not None
        capacity_and_resource.refresh_from_db()
        assert capacity_and_resource.dashboards.count() == 1
