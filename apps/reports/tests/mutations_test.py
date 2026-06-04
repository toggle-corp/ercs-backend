import typing
from unittest.mock import patch

from apps.reports.factories import LinkFactory, ReportFactory, ThematicAreaFactory
from apps.reports.models import Link, Report
from apps.users.factories import UserFactory
from apps.users.models import User
from main.tests import TestCase


class TestReportMutations(TestCase):
    class Mutation:
        DELETE_REPORT = """
            mutation DeleteReport($id: ID!) {
                deleteReport(id: $id) {
                    ... on ReportTypeMutationResponseType {
                        ok
                        errors
                    }
                }
            }
        """

        CREATE_LINK = """
            mutation CreateLink($data: LinkCreateInput!) {
                createLink(data: $data) {
                    ... on LinkTypeMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            title
                            url
                            linkType
                        }
                    }
                }
            }
        """

        UPDATE_LINK = """
            mutation UpdateLink($id: ID!, $data: LinkUpdateInput!) {
                updateLink(id: $id, data: $data) {
                    ... on LinkTypeMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            title
                        }
                    }
                }
            }
        """

        DELETE_LINK = """
            mutation DeleteLink($id: ID!) {
                deleteLink(id: $id) {
                    ... on LinkTypeMutationResponseType {
                        ok
                        errors
                    }
                }
            }
        """
        CREATE_REPORT = """
            mutation CreateReport($data: ReportCreateInput!) {
                createReport(data: $data) {
                    ... on ReportTypeMutationResponseType{


                    ok
                    errors
                    result {
                        id
                        title
                        contentType
                        visibility
                        iframeUrl
                    }
                }
            }
        }
        """

        UPDATE_REPORT = """
            mutation UpdateReport($id: ID!, $data: ReportUpdateInput!) {
                updateReport(id: $id, data: $data) {
                    ... on ReportTypeMutationResponseType{


                    ok
                    errors
                    result {
                        id
                        title
                        visibility
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
        cls.staff = UserFactory.create(role=User.Role.STAFF)
        cls.thematic_area = ThematicAreaFactory.create()

    def test_create_iframe_report(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_REPORT,
            variables={
                "data": {
                    "title": "Test Report",
                    "contentType": Report.ContentType.IFRAME,
                    "iframeUrl": "https://app.powerbi.com/embed/123",
                    "thematicArea": str(self.thematic_area.pk),
                },
            },
        )
        resp = content["data"]["createReport"]
        assert resp["ok"] is True
        assert resp["errors"] is None
        assert resp["result"]["title"] == "Test Report"
        assert resp["result"]["contentType"] == Report.ContentType.IFRAME
        assert resp["result"]["visibility"] == Report.Visibility.PUBLIC

    def test_create_report_requires_auth(self):
        self.logout()
        content = self.query_check(
            self.Mutation.CREATE_REPORT,
            assert_errors=True,
            variables={
                "data": {
                    "title": "Unauthorized",
                    "contentType": Report.ContentType.IFRAME,
                    "iframeUrl": "https://example.com/embed",
                    "thematicArea": str(self.thematic_area.pk),
                },
            },
        )
        assert "errors" in content

    def test_cannot_change_private_to_public(self):
        self.force_login(self.user)
        private_report = ReportFactory.create(
            visibility=Report.Visibility.PRIVATE,
            uploaded_by=self.user,
        )
        content = self.query_check(
            self.Mutation.UPDATE_REPORT,
            variables={
                "id": str(private_report.pk),
                "data": {"visibility": Report.Visibility.PUBLIC},
            },
        )
        resp = content["data"]["updateReport"]
        assert resp["ok"] is False
        assert resp["errors"] is not None

    # ------------------------------------------------------------------
    # deleteReport
    # ------------------------------------------------------------------

    def test_authenticated_can_delete_report(self):
        self.force_login(self.user)
        report = ReportFactory.create(uploaded_by=self.user)
        content = self.query_check(
            self.Mutation.DELETE_REPORT,
            variables={"id": self.gID(report.pk)},
        )
        resp = content["data"]["deleteReport"]
        assert resp["ok"] is True
        assert not Report.objects.filter(pk=report.pk).exists()

    def test_unauthenticated_cannot_delete_report(self):
        self.logout()
        report = ReportFactory.create(uploaded_by=self.user)
        content = self.query_check(
            self.Mutation.DELETE_REPORT,
            assert_errors=True,
            variables={"id": self.gID(report.pk)},
        )
        assert "errors" in content

    # ------------------------------------------------------------------
    # Document extraction triggered on REPORT-type create
    # ------------------------------------------------------------------

    def test_create_report_type_report_triggers_extraction(self):
        self.force_login(self.user)
        with patch("apps.reports.graphql.mutations.trigger_document_extraction") as mock_trigger:
            mock_trigger.return_value = None
            content = self.query_check(
                self.Mutation.CREATE_REPORT,
                variables={
                    "data": {
                        "title": "AI Report",
                        "contentType": Report.ContentType.IFRAME,
                        "iframeUrl": "https://example.com/embed",
                        "thematicArea": str(self.thematic_area.pk),
                        "reportType": Report.ReportType.REPORT,
                    },
                },
            )
        resp = content["data"]["createReport"]
        assert resp["ok"] is True
        mock_trigger.assert_called_once()

    def test_create_non_report_type_skips_extraction(self):
        self.force_login(self.user)
        with patch("apps.reports.graphql.mutations.trigger_document_extraction") as mock_trigger:
            mock_trigger.return_value = None
            content = self.query_check(
                self.Mutation.CREATE_REPORT,
                variables={
                    "data": {
                        "title": "A Manual",
                        "contentType": Report.ContentType.IFRAME,
                        "iframeUrl": "https://example.com/embed",
                        "thematicArea": str(self.thematic_area.pk),
                        "reportType": Report.ReportType.MANUAL,
                    },
                },
            )
        resp = content["data"]["createReport"]
        assert resp["ok"] is True
        mock_trigger.assert_not_called()

    # ------------------------------------------------------------------
    # createLink / updateLink / deleteLink
    # ------------------------------------------------------------------

    def test_staff_can_create_link(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.CREATE_LINK,
            variables={
                "data": {
                    "title": "IFRC GO",
                    "url": "https://go.ifrc.org",
                    "linkType": Link.LinkType.EXTERNAL,
                },
            },
        )
        resp = content["data"]["createLink"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "IFRC GO"
        assert resp["result"]["linkType"] == Link.LinkType.EXTERNAL

    def test_viewer_cannot_create_link(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_LINK,
            assert_errors=True,
            variables={
                "data": {
                    "title": "Blocked",
                    "url": "https://example.com",
                    "linkType": Link.LinkType.EXTERNAL,
                },
            },
        )
        assert "errors" in content

    def test_staff_can_update_link(self):
        self.force_login(self.staff)
        link = LinkFactory.create()
        content = self.query_check(
            self.Mutation.UPDATE_LINK,
            variables={"id": self.gID(link.pk), "data": {"title": "Updated Title"}},
        )
        resp = content["data"]["updateLink"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "Updated Title"

    def test_staff_can_delete_link(self):
        self.force_login(self.staff)
        link = LinkFactory.create()
        content = self.query_check(
            self.Mutation.DELETE_LINK,
            variables={"id": self.gID(link.pk)},
        )
        resp = content["data"]["deleteLink"]
        assert resp["ok"] is True
        assert not Link.objects.filter(pk=link.pk).exists()
