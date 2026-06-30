import typing

from apps.reports.factories import DocumentExtractionFactory, ReportFactory
from apps.reports.models import DocumentExtraction, Report
from apps.users.factories import UserFactory
from main.tests import TestCase


class TestReportQueries(TestCase):
    class Query:
        REPORTS = """
            query Reports($pagination: OffsetPaginationInput, $filters: ReportFilter) {
                reports(pagination: $pagination, filters: $filters) {
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


class TestReportSummaryQuery(TestCase):
    class Query:
        REPORT_SUMMARIES = """
            query ReportSummaries($pagination: OffsetPaginationInput, $filters: ReportSummaryFilter) {
                reportSummaries(pagination: $pagination, filters: $filters) {
                    totalCount
                    pageInfo { offset limit }
                    results {
                        id
                        text
                        pageNumber
                        chunkType
                        status
                    }
                }
            }
        """

        REPORT_SUMMARY = """
            query ReportSummary($id: ID!) {
                reportSummary(id: $id) {
                    id
                    text
                    pageNumber
                    chunkType
                    status
                }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.extraction_summary = DocumentExtractionFactory.create(
            chunk_type=DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY,
            status=DocumentExtraction.Status.SUCCESS,
        )
        cls.extraction_content = DocumentExtractionFactory.create(
            chunk_type=DocumentExtraction.ExtractionType.EXTRACTED_CONTENT,
            status=DocumentExtraction.Status.PENDING,
        )

    def test_requires_authentication(self):
        content = self.query_check(
            self.Query.REPORT_SUMMARIES,
            assert_errors=True,
            variables={"pagination": {"limit": 10, "offset": 0}},
        )
        assert "errors" in content

    def test_authenticated_returns_all(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Query.REPORT_SUMMARIES,
            variables={"pagination": {"limit": 10, "offset": 0}},
        )
        assert content["data"]["reportSummaries"]["totalCount"] == 2

    def test_filter_by_chunk_type(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Query.REPORT_SUMMARIES,
            variables={
                "pagination": {"limit": 10, "offset": 0},
                "filters": {"chunkType": DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY.name},
            },
        )
        results = content["data"]["reportSummaries"]["results"]
        assert len(results) == 1
        assert results[0]["chunkType"] == DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY.name

    def test_filter_by_status(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Query.REPORT_SUMMARIES,
            variables={
                "pagination": {"limit": 10, "offset": 0},
                "filters": {"status": DocumentExtraction.Status.SUCCESS.name},
            },
        )
        results = content["data"]["reportSummaries"]["results"]
        assert len(results) == 1
        assert results[0]["status"] == DocumentExtraction.Status.SUCCESS.name

    def test_filter_by_id(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Query.REPORT_SUMMARIES,
            variables={
                "pagination": {"limit": 10, "offset": 0},
                "filters": {"id": self.gID(self.extraction_summary.pk)},
            },
        )
        results = content["data"]["reportSummaries"]["results"]
        assert len(results) == 1
        assert results[0]["id"] == self.gID(self.extraction_summary.pk)

    def test_pagination(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Query.REPORT_SUMMARIES,
            variables={"pagination": {"limit": 1, "offset": 0}},
        )
        data = content["data"]["reportSummaries"]
        assert data["totalCount"] == 2
        assert len(data["results"]) == 1
        assert data["pageInfo"]["limit"] == 1

    def test_single_report_summary(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Query.REPORT_SUMMARY,
            variables={"id": self.gID(self.extraction_summary.pk)},
        )
        result = content["data"]["reportSummary"]
        assert result["id"] == self.gID(self.extraction_summary.pk)
        assert result["chunkType"] == DocumentExtraction.ExtractionType.DOCUMENT_SUMMARY.name
        assert result["status"] == DocumentExtraction.Status.SUCCESS.name
