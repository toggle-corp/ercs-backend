import typing

from apps.reports.factories import ReportFactory
from apps.reports.models import Report
from apps.users.factories import UserFactory
from main.tests import TestCase


class TestReportMutations(TestCase):
    class Mutation:
        CREATE_REPORT = """
            mutation CreateReport($data: ReportCreateInput!) {
                createReport(data: $data) {
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
        """

        UPDATE_REPORT = """
            mutation UpdateReport($id: ID!, $data: ReportUpdateInput!) {
                updateReport(id: $id, data: $data) {
                    ok
                    errors
                    result {
                        id
                        title
                        visibility
                    }
                }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()

    def test_create_iframe_report(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_REPORT,
            variables={
                "data": {
                    "title": "Test Report",
                    "contentType": Report.ContentType.IFRAME,
                    "iframeUrl": "https://app.powerbi.com/embed/123",
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
