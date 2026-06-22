import typing

from apps.dashboards.factories import CapacityAndResourceFactory, ExternalDashboardFactory
from apps.dashboards.models import CapacityAndResource, ExternalDashboard
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
                        capacityAndResourceId
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
                        capacityAndResourceId
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
        cls.capacity = CapacityAndResourceFactory.create()

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
        assert resp["result"]["capacityAndResourceId"] is None

    def test_create_dashboard_linked_to_capacity(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.CREATE_DASHBOARD,
            variables={
                "data": {
                    "title": "WASH Capacity Dashboard",
                    "url": "https://app.powerbi.com/embed/wash",
                    "page": ExternalDashboard.Page.CAPACITY_RESOURCES.name,
                    "capacityAndResource": str(self.capacity.pk),
                },
            },
        )
        resp = content["data"]["createExternalDashboard"]
        assert resp["ok"] is True
        assert resp["result"]["capacityAndResourceId"] == str(self.capacity.pk)

    def test_create_dashboard_wrong_page_for_capacity(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.CREATE_DASHBOARD,
            variables={
                "data": {
                    "title": "Bad Link",
                    "url": "https://app.powerbi.com/embed/bad",
                    "page": ExternalDashboard.Page.OPERATIONS.name,
                    "capacityAndResource": str(self.capacity.pk),
                },
            },
        )
        resp = content["data"]["createExternalDashboard"]
        assert resp["ok"] is False
        assert resp["errors"] is not None

    def test_update_dashboard_link_to_capacity(self):
        self.force_login(self.staff)
        db = ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.CAPACITY_RESOURCES,
            created_by=self.staff,
        )
        content = self.query_check(
            self.Mutation.UPDATE_DASHBOARD,
            variables={
                "id": str(db.pk),
                "data": {"capacityAndResource": str(self.capacity.pk)},
            },
        )
        resp = content["data"]["updateExternalDashboard"]
        assert resp["ok"] is True
        assert resp["result"]["capacityAndResourceId"] == str(self.capacity.pk)

    def test_update_dashboard_wrong_page_for_capacity(self):
        self.force_login(self.staff)
        db = ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.HOME,
            created_by=self.staff,
        )
        content = self.query_check(
            self.Mutation.UPDATE_DASHBOARD,
            variables={
                "id": str(db.pk),
                "data": {"capacityAndResource": str(self.capacity.pk)},
            },
        )
        resp = content["data"]["updateExternalDashboard"]
        assert resp["ok"] is False
        assert resp["errors"] is not None

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
    def setUpClass(cls):
        super().setUpClass()
        cls.staff = UserFactory.create(role=User.Role.STAFF)
        cls.viewer = UserFactory.create(role=User.Role.VIEWER)

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
                },
            },
        )
        resp = content["data"]["createCapacityAndResource"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "Water & Sanitation"
        assert resp["result"]["dashboards"] == []

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

    def test_update_capacity_and_resource(self):
        self.force_login(self.staff)
        instance = CapacityAndResourceFactory.create(is_active=True, order=50)
        content = self.query_check(
            self.Mutation.UPDATE_CAPACITY_AND_RESOURCE,
            variables={
                "id": str(instance.pk),
                "data": {
                    "title": "Updated Title",
                    "isActive": False,
                },
            },
        )
        resp = content["data"]["updateCapacityAndResource"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "Updated Title"
        assert resp["result"]["isActive"] is False

        instance.refresh_from_db()
        assert instance.title == "Updated Title"

    def test_dashboards_appear_via_fk(self):
        """Dashboards linked via FK show up under the capacity entry."""
        self.force_login(self.staff)
        instance = CapacityAndResourceFactory.create(is_active=True, order=60)
        ExternalDashboardFactory.create(
            page=ExternalDashboard.Page.CAPACITY_RESOURCES,
            capacity_and_resource=instance,
        )
        content = self.query_check(
            self.Mutation.UPDATE_CAPACITY_AND_RESOURCE,
            variables={"id": str(instance.pk), "data": {"title": instance.title}},
        )
        resp = content["data"]["updateCapacityAndResource"]
        assert resp["ok"] is True
        assert len(resp["result"]["dashboards"]) == 1

    def test_capacity_and_resource_pk(self):
        """Verifies CapacityAndResource is created and pk can be used."""
        instance = CapacityAndResourceFactory.create()
        assert CapacityAndResource.objects.filter(pk=instance.pk).exists()
