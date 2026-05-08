# apps/dashboards/tests/test_mutations.py
import typing

from apps.dashboards.factories import CapacityAndResourceFactory, ExternalDashboardFactory
from apps.dashboards.models import CapacityAndResourceIframeUrl, ExternalDashboard
from apps.users.factories import UserFactory
from apps.users.models import User
from main.tests import TestCase


class TestExternalDashboardMutations(TestCase):
    class Mutation:
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
                    "page": ExternalDashboard.Page.OPERATIONS,
                },
            },
        )
        resp = content["data"]["createExternalDashboard"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "Operations KPIs"
        assert resp["result"]["page"] == ExternalDashboard.Page.OPERATIONS

    def test_viewer_cannot_create(self):
        self.force_login(self.viewer)
        content = self.query_check(
            self.Mutation.CREATE_DASHBOARD,
            assert_errors=True,
            variables={
                "data": {
                    "title": "Blocked",
                    "url": "https://example.com",
                    "page": ExternalDashboard.Page.HOME,
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
                            iframeUrls {
                                id
                                order
                                dashboard {
                                    id
                                    title
                                    page
                                }
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
                            iframeUrls {
                                id
                                order
                                dashboard {
                                    id
                                    title
                                }
                            }
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

        cls.dashboard_1 = ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.CAPACITY_RESOURCES,
            order=0,
        )
        cls.dashboard_2 = ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.CAPACITY_RESOURCES,
            order=1,
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
                    "order": 0,
                    "iframeUrls": [
                        {"dashboard": str(self.dashboard_1.pk), "order": 0},
                        {"dashboard": str(self.dashboard_2.pk), "order": 1},
                    ],
                },
            },
        )
        resp = content["data"]["createCapacityAndResource"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "Water & Sanitation"
        assert len(resp["result"]["iframeUrls"]) == 2
        assert resp["result"]["iframeUrls"][0]["dashboard"]["page"] == ExternalDashboard.Page.CAPACITY_RESOURCES

    def test_create_without_iframe_urls_fails(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.CREATE_CAPACITY_AND_RESOURCE,
            variables={
                "data": {
                    "title": "Empty Capacity",
                    "isActive": True,
                    "order": 1,
                    "iframeUrls": [],
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

    def test_update_capacity_and_resource(self):
        self.force_login(self.staff)
        instance = CapacityAndResourceFactory.create(is_active=True)
        content = self.query_check(
            self.Mutation.UPDATE_CAPACITY_AND_RESOURCE,
            variables={
                "id": str(instance.pk),
                "data": {"title": "Updated Title", "isActive": False},
            },
        )
        resp = content["data"]["updateCapacityAndResource"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "Updated Title"
        assert resp["result"]["isActive"] is False

    def test_update_iframe_urls_replaces_existing(self):
        self.force_login(self.staff)
        instance = CapacityAndResourceFactory.create(is_active=True)

        CapacityAndResourceIframeUrl.objects.create(
            capacity_and_resource=instance,
            dashboard=self.dashboard_1,
            order=0,
        )

        content = self.query_check(
            self.Mutation.UPDATE_CAPACITY_AND_RESOURCE,
            variables={
                "id": str(instance.pk),
                "data": {
                    "iframeUrls": [
                        {"dashboard": str(self.dashboard_2.pk), "order": 0},
                    ],
                },
            },
        )
        resp = content["data"]["updateCapacityAndResource"]
        assert resp["ok"] is True
        assert len(resp["result"]["iframeUrls"]) == 1
        assert resp["result"]["iframeUrls"][0]["dashboard"]["id"] == str(self.dashboard_2.pk)

    def test_deactivate_capacity_and_resource(self):
        self.force_login(self.staff)
        instance = CapacityAndResourceFactory.create(is_active=True)
        content = self.query_check(
            self.Mutation.UPDATE_CAPACITY_AND_RESOURCE,
            variables={
                "id": str(instance.pk),
                "data": {"isActive": False},
            },
        )
        resp = content["data"]["updateCapacityAndResource"]
        assert resp["ok"] is True
        assert resp["result"]["isActive"] is False
