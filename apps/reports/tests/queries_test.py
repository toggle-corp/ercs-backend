import typing

from apps.reports.factories import ReportFactory
from apps.reports.models import Report
from apps.users.factories import UserFactory
from main.tests import TestCase


class TestReportQueries(TestCase):
    class Query:
        REPORTS = """
            query Reports($pagination: OffsetPaginationInput, $filters: ReportFilter) {
                reports(pagination: $pagination, filters: $filters, order: {createdAt: DESC}) {
                    totalCount
                    pageInfo { offset limit }
                    results {
                        id
                        title
                        contentType
                        visibility
                        iframeUrl
                        thematicAreaId
                        disasterType
                        owner
                        uploadedById
                        publishedAt
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
        cls.public_report = ReportFactory.create(
            title="Public Report",
            visibility=Report.Visibility.PUBLIC,
            uploaded_by=cls.user,
        )
        cls.private_report = ReportFactory.create(
            title="Private Report",
            visibility=Report.Visibility.PRIVATE,
            uploaded_by=cls.user,
        )

    def test_reports_query(self):
        content = self.query_check(
            self.Query.REPORTS,
            variables={"pagination": {"limit": 10, "offset": 0}},
        )
        assert content["data"]["reports"]["totalCount"] == 2

    def test_filter_by_visibility(self):
        content = self.query_check(
            self.Query.REPORTS,
            variables={
                "pagination": {"limit": 10, "offset": 0},
                "filters": {"visibility": Report.Visibility.PUBLIC.name},
            },
        )
        results = content["data"]["reports"]["results"]
        assert len(results) == 1
        assert results[0]["title"] == "Public Report"
