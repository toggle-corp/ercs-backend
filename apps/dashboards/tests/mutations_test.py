import typing
import uuid

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
                        capacityAndResourceId
                    }
                }
            }
        }
        """

        DELETE_DASHBOARD = """
            mutation DeleteExternalDashboard($id: ID!) {
                deleteExternalDashboard(id: $id) {
                    ok
                    errors
                }
            }
        """

        BULK_UPDATE_ORDER = """
            mutation BulkUpdateExternalDashboards($data: [ExternalDashboardOrderInput!]!) {
                bulkUpdateExternalDashboards(data: $data) {
                    ... on ExternalDashboardTypeListMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            order
                            page
                        }
                    }
                }
            }
        """

        BULK_UPDATE_ORDER_OPERATION_INFO = """
            mutation BulkUpdateExternalDashboards($data: [ExternalDashboardOrderInput!]!) {
                bulkUpdateExternalDashboards(data: $data) {
                    ... on OperationInfo {
                        messages {
                            kind
                            message
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
                        showOnHome
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

    def test_create_dashboard_show_on_home_requires_active(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.CREATE_DASHBOARD,
            variables={
                "data": {
                    "title": "Inactive Home Dashboard",
                    "url": "https://app.powerbi.com/embed/inactive",
                    "page": ExternalDashboard.Page.HOME.name,
                    "showOnHome": True,
                    "isActive": False,
                },
            },
        )
        resp = content["data"]["createExternalDashboard"]
        assert resp["ok"] is True

    def test_update_dashboard_deactivate_while_show_on_home(self):
        self.force_login(self.staff)
        dashboard = ExternalDashboardFactory.create(is_active=True, show_on_home=True, created_by=self.staff)
        content = self.query_check(
            self.Mutation.UPDATE_DASHBOARD,
            variables={"id": str(dashboard.pk), "data": {"isActive": False}},
        )
        resp = content["data"]["updateExternalDashboard"]
        assert resp["ok"] is True
        assert resp["result"]["isActive"] is False
        assert resp["result"]["showOnHome"] is False

    def test_viewer_cannot_create(self):
        self.force_login(self.viewer)
        content = self.query_check(
            self.Mutation.CREATE_DASHBOARD,
            variables={
                "data": {
                    "title": "Blocked",
                    "url": "https://example.com",
                    "page": ExternalDashboard.Page.HOME.name,
                },
            },
        )
        self.assert_permission_denied(content, "createExternalDashboard")

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
            variables={"id": str(dashboard.pk)},
        )
        self.assert_permission_denied(content, "addDashboardToHome")

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

    def test_bulk_update_dashboard_order(self):
        self.force_login(self.staff)
        first, second, third = (
            ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=order) for order in (1, 2, 3)
        )
        content = self.query_check(
            self.Mutation.BULK_UPDATE_ORDER,
            variables={
                "data": [
                    {"id": str(first.pk), "order": 3},
                    {"id": str(second.pk), "order": 1},
                    {"id": str(third.pk), "order": 2},
                ],
            },
        )
        resp = content["data"]["bulkUpdateExternalDashboards"]
        assert resp["ok"] is True
        assert resp["errors"] is None
        assert [item["id"] for item in resp["result"]] == [str(second.pk), str(third.pk), str(first.pk)]
        assert [item["order"] for item in resp["result"]] == [1, 2, 3]

        for dashboard, expected_order in ((first, 3), (second, 1), (third, 2)):
            dashboard.refresh_from_db()
            assert dashboard.order == expected_order

    def test_bulk_update_dashboard_order_partial_subset(self):
        """Dashboards left out of the payload keep their existing order."""
        self.force_login(self.staff)
        target = ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=1)
        untouched = ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=7)
        content = self.query_check(
            self.Mutation.BULK_UPDATE_ORDER,
            variables={"data": [{"id": str(target.pk), "order": 4}]},
        )
        resp = content["data"]["bulkUpdateExternalDashboards"]
        assert resp["ok"] is True
        assert len(resp["result"]) == 1

        target.refresh_from_db()
        untouched.refresh_from_db()
        assert target.order == 4
        assert untouched.order == 7

    def test_bulk_update_dashboard_order_result_sorted_across_pages(self):
        self.force_login(self.staff)
        operations = ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=1)
        home = ExternalDashboardFactory.create(page=ExternalDashboard.Page.HOME, order=9)
        content = self.query_check(
            self.Mutation.BULK_UPDATE_ORDER,
            variables={
                "data": [
                    {"id": str(operations.pk), "order": 1},
                    {"id": str(home.pk), "order": 2},
                ],
            },
        )
        resp = content["data"]["bulkUpdateExternalDashboards"]
        assert resp["ok"] is True
        # HOME (10) sorts before OPERATIONS (20) regardless of order value
        assert [item["page"] for item in resp["result"]] == [
            ExternalDashboard.Page.HOME.name,
            ExternalDashboard.Page.OPERATIONS.name,
        ]
        assert [item["id"] for item in resp["result"]] == [str(home.pk), str(operations.pk)]

    def test_bulk_update_dashboard_order_unknown_id(self):
        """An id that does not exist fails the whole batch and writes nothing."""
        self.force_login(self.staff)
        dashboard = ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=1)
        missing_id = str(uuid.uuid4())
        content = self.query_check(
            self.Mutation.BULK_UPDATE_ORDER,
            variables={
                "data": [
                    {"id": str(dashboard.pk), "order": 5},
                    {"id": missing_id, "order": 6},
                ],
            },
        )
        resp = content["data"]["bulkUpdateExternalDashboards"]
        assert resp["ok"] is False
        assert resp["errors"] is not None
        assert resp["result"] is None

        dashboard.refresh_from_db()
        assert dashboard.order == 1

    def test_bulk_update_dashboard_order_empty_data(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.BULK_UPDATE_ORDER,
            variables={"data": []},
        )
        resp = content["data"]["bulkUpdateExternalDashboards"]
        assert resp["ok"] is True
        assert resp["result"] == []

    def test_bulk_update_dashboard_order_duplicate_ids(self):
        """Current behaviour: duplicate ids collapse silently and the last order wins."""
        self.force_login(self.staff)
        dashboard = ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=1)
        content = self.query_check(
            self.Mutation.BULK_UPDATE_ORDER,
            variables={
                "data": [
                    {"id": str(dashboard.pk), "order": 2},
                    {"id": str(dashboard.pk), "order": 3},
                ],
            },
        )
        resp = content["data"]["bulkUpdateExternalDashboards"]
        assert resp["ok"] is True
        assert len(resp["result"]) == 1

        dashboard.refresh_from_db()
        assert dashboard.order == 3

    def test_bulk_update_dashboard_order_unparsable_id(self):
        """An id that is not a valid UUID comes back as an OperationInfo payload, not a reorder."""
        self.force_login(self.staff)
        dashboard = ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=1)
        content = self.query_check(
            self.Mutation.BULK_UPDATE_ORDER_OPERATION_INFO,
            variables={
                "data": [
                    {"id": str(dashboard.pk), "order": 5},
                    {"id": "not-a-uuid", "order": 6},
                ],
            },
        )
        resp = content["data"]["bulkUpdateExternalDashboards"]
        assert resp["messages"]

        dashboard.refresh_from_db()
        assert dashboard.order == 1

    def test_bulk_update_dashboard_order_negative_order(self):
        """Current behaviour: `order` is not validated, so a negative value hits the db constraint."""
        self.force_login(self.staff)
        dashboard = ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=1)
        content = self.query_check(
            self.Mutation.BULK_UPDATE_ORDER,
            assert_errors=True,
            variables={"data": [{"id": str(dashboard.pk), "order": -1}]},
        )
        assert "errors" in content

    def test_viewer_cannot_bulk_update_dashboard_order(self):
        self.force_login(self.viewer)
        dashboard = ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=1)
        content = self.query_check(
            self.Mutation.BULK_UPDATE_ORDER,
            variables={"data": [{"id": str(dashboard.pk), "order": 2}]},
        )
        self.assert_permission_denied(content, "bulkUpdateExternalDashboards")

        dashboard.refresh_from_db()
        assert dashboard.order == 1

    def test_anonymous_cannot_bulk_update_dashboard_order(self):
        self.logout()
        dashboard = ExternalDashboardFactory.create(page=ExternalDashboard.Page.OPERATIONS, order=1)
        content = self.query_check(
            self.Mutation.BULK_UPDATE_ORDER,
            variables={"data": [{"id": str(dashboard.pk), "order": 2}]},
        )
        self.assert_permission_denied(content, "bulkUpdateExternalDashboards")

        dashboard.refresh_from_db()
        assert dashboard.order == 1

    def test_viewer_cannot_remove_from_home(self):
        self.force_login(self.viewer)
        dashboard = ExternalDashboardFactory.create(show_on_home=True)
        content = self.query_check(
            self.Mutation.REMOVE_FROM_HOME,
            variables={"id": str(dashboard.pk)},
        )
        self.assert_permission_denied(content, "removeDashboardFromHome")

    def test_staff_can_delete_dashboard(self):
        self.force_login(self.staff)
        dashboard = ExternalDashboardFactory.create(created_by=self.staff)
        content = self.query_check(
            self.Mutation.DELETE_DASHBOARD,
            variables={"id": str(dashboard.pk)},
        )
        resp = content["data"]["deleteExternalDashboard"]
        assert resp["ok"] is True, resp
        assert not ExternalDashboard.objects.filter(pk=dashboard.pk).exists()

    def test_viewer_cannot_delete_dashboard(self):
        self.force_login(self.viewer)
        dashboard = ExternalDashboardFactory.create(created_by=self.staff)
        content = self.query_check(
            self.Mutation.DELETE_DASHBOARD,
            variables={"id": str(dashboard.pk)},
        )
        self.assert_permission_denied(content, "deleteExternalDashboard")
        assert ExternalDashboard.objects.filter(pk=dashboard.pk).exists()

    def test_deleting_missing_dashboard_is_reported_on_the_payload(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.DELETE_DASHBOARD,
            variables={"id": str(uuid.uuid4())},
        )
        resp = content["data"]["deleteExternalDashboard"]
        assert resp["ok"] is False, resp
        assert resp["errors"][0]["messages"] == (
            "This External Dashboard no longer exists. It may already have been deleted."
        )


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

        DELETE_CAPACITY_AND_RESOURCE = """
            mutation DeleteCapacityAndResource($id: ID!) {
                deleteCapacityAndResource(id: $id) {
                    ok
                    errors
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
            variables={
                "data": {
                    "title": "Blocked",
                    "isActive": True,
                    "order": 0,
                },
            },
        )
        self.assert_permission_denied(content, "createCapacityAndResource")

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

    def test_viewer_cannot_delete_capacity_and_resource(self):
        self.force_login(self.viewer)
        instance = CapacityAndResourceFactory.create()
        content = self.query_check(
            self.Mutation.DELETE_CAPACITY_AND_RESOURCE,
            variables={"id": str(instance.pk)},
        )
        self.assert_permission_denied(content, "deleteCapacityAndResource")
        assert CapacityAndResource.objects.filter(pk=instance.pk).exists()

    def test_staff_can_delete_capacity_and_resource_with_linked_dashboard(self):
        self.force_login(self.staff)
        instance = CapacityAndResourceFactory.create()
        dashboard = ExternalDashboardFactory.create(capacity_and_resource=instance, created_by=self.staff)
        content = self.query_check(
            self.Mutation.DELETE_CAPACITY_AND_RESOURCE,
            variables={"id": str(instance.pk)},
        )
        resp = content["data"]["deleteCapacityAndResource"]
        assert resp["ok"] is True, resp
        assert not CapacityAndResource.objects.filter(pk=instance.pk).exists()
        dashboard.refresh_from_db()
        assert dashboard.capacity_and_resource is None
