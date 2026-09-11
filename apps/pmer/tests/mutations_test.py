import typing

from django.core.files.uploadedfile import SimpleUploadedFile

from apps.geo.factories import RegionFactory
from apps.pmer.factories import PmerReportFactory
from apps.pmer.models import PmerReport
from apps.users.factories import UserFactory
from main.tests import TestCase


def pdf_upload(name: str = "pmer-report.pdf") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, b"%PDF-1.4 pmer report", content_type="application/pdf")


class TestPmerReportMutations(TestCase):
    class Mutation:
        CREATE_PMER_REPORT = """
            mutation CreatePmerReport($data: PmerReportCreateInput!) {
                createPmerReport(data: $data) {
                    ... on PmerReportTypeMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            title
                            description
                            category
                            categoryDisplay
                            reportType
                            reportTypeDisplay
                            visibility
                            visibilityDisplay
                            department
                            project
                            region { id name }
                            file { name size url }
                            createdBy { id email }
                        }
                    }
                }
            }
        """

        UPDATE_PMER_REPORT = """
            mutation UpdatePmerReport($id: ID!, $data: PmerReportUpdateInput!) {
                updatePmerReport(id: $id, data: $data) {
                    ... on PmerReportTypeMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            title
                            description
                            category
                            reportType
                            visibility
                            department
                            project
                            region { id name }
                        }
                    }
                }
            }
        """

        DELETE_PMER_REPORT = """
            mutation DeletePmerReport($id: ID!) {
                deletePmerReport(id: $id) {
                    ok
                    errors
                }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.other_user = UserFactory.create()
        cls.region = RegionFactory.create(name="Amhara")

    def create_pmer_report(
        self,
        *,
        title: str,
        category: PmerReport.Category,
        report_type: PmerReport.DocumentType = PmerReport.DocumentType.ANNUAL_REPORT,
        description: str | None = None,
        department: str | None = None,
        project: str | None = None,
        region: str | None = None,
        visibility: PmerReport.Visibility | None = None,
        file: SimpleUploadedFile | None = None,
        assert_errors: bool = False,
    ) -> dict[str, typing.Any]:
        data: dict[str, typing.Any] = {
            "title": title,
            "category": self.genum(category),
            "reportType": self.genum(report_type),
            "file": None,
        }
        if description is not None:
            data["description"] = description
        if department is not None:
            data["department"] = department
        if project is not None:
            data["project"] = project
        if region is not None:
            data["region"] = region
        if visibility is not None:
            data["visibility"] = self.genum(visibility)
        return self.query_check(
            self.Mutation.CREATE_PMER_REPORT,
            assert_errors=assert_errors,
            variables={"data": data},
            files={"0": file or pdf_upload()},
            map={"0": ["variables.data.file"]},
        )

    def test_create_pmer_report(self):
        self.force_login(self.user)
        content = self.create_pmer_report(
            title="DRR Baseline Study",
            category=PmerReport.Category.DRR,
            report_type=PmerReport.DocumentType.MID_TERM_REVIEW_REPORT,
            description="Baseline assessment for DRR programming.",
            department="Disaster Risk Reduction",
            project="Community Resilience",
            region=str(self.region.pk),
            visibility=PmerReport.Visibility.PRIVATE,
        )
        resp = content["data"]["createPmerReport"]
        assert resp["ok"] is True, resp
        assert resp["errors"] is None
        assert resp["result"]["title"] == "DRR Baseline Study"
        assert resp["result"]["description"] == "Baseline assessment for DRR programming."
        assert resp["result"]["category"] == self.genum(PmerReport.Category.DRR)
        assert resp["result"]["categoryDisplay"] == "DRR (Disaster Risk Reduction)"
        assert resp["result"]["reportType"] == self.genum(PmerReport.DocumentType.MID_TERM_REVIEW_REPORT)
        assert resp["result"]["reportTypeDisplay"] == "Mid-term Review Report"
        assert resp["result"]["visibility"] == self.genum(PmerReport.Visibility.PRIVATE)
        assert resp["result"]["visibilityDisplay"] == "Private"
        assert resp["result"]["department"] == "Disaster Risk Reduction"
        assert resp["result"]["project"] == "Community Resilience"
        assert resp["result"]["region"] == {"id": str(self.region.pk), "name": "Amhara"}
        assert resp["result"]["file"]["name"].endswith(".pdf")
        assert resp["result"]["createdBy"]["id"] == str(self.user.pk)

    def test_create_pmer_report_without_optional_fields(self):
        self.force_login(self.user)
        content = self.create_pmer_report(title="Minimal Report", category=PmerReport.Category.DPR)
        resp = content["data"]["createPmerReport"]
        assert resp["ok"] is True, resp
        assert resp["result"]["description"] is None
        assert resp["result"]["department"] is None
        assert resp["result"]["project"] is None
        assert resp["result"]["region"] is None
        # `visibility` defaults to PUBLIC in the input and on the model
        assert resp["result"]["visibility"] == self.genum(PmerReport.Visibility.PUBLIC)

    def test_create_pmer_report_requires_auth(self):
        self.logout()
        content = self.create_pmer_report(
            title="Unauthorized",
            category=PmerReport.Category.DPR,
        )
        self.assert_permission_denied(content, "createPmerReport")
        assert not PmerReport.objects.filter(title="Unauthorized").exists()

    def test_create_pmer_report_rejects_unsupported_file_type(self):
        self.force_login(self.user)
        content = self.create_pmer_report(
            title="Bad File",
            category=PmerReport.Category.DPR,
            file=SimpleUploadedFile("payload.exe", b"MZ", content_type="application/octet-stream"),
        )
        resp = content["data"]["createPmerReport"]
        assert resp["ok"] is False, resp
        assert resp["errors"] is not None
        assert not PmerReport.objects.filter(title="Bad File").exists()

    def test_create_pmer_report_for_each_category(self):
        self.force_login(self.user)
        for category in PmerReport.Category:
            content = self.create_pmer_report(title=f"Report {category.name}", category=category)
            resp = content["data"]["createPmerReport"]
            assert resp["ok"] is True, resp
            assert resp["result"]["category"] == self.genum(category)

    def test_create_pmer_report_for_each_report_type(self):
        self.force_login(self.user)
        for report_type in PmerReport.DocumentType:
            content = self.create_pmer_report(
                title=f"Report {report_type.name}",
                category=PmerReport.Category.DPR,
                report_type=report_type,
            )
            resp = content["data"]["createPmerReport"]
            assert resp["ok"] is True, resp
            assert resp["result"]["reportType"] == self.genum(report_type)
            assert resp["result"]["reportTypeDisplay"] == report_type.label

    def test_create_pmer_report_requires_report_type(self):
        self.force_login(self.user)
        content = self.query_check(
            self.Mutation.CREATE_PMER_REPORT,
            assert_errors=True,
            variables={
                "data": {
                    "title": "No Report Type",
                    "category": self.genum(PmerReport.Category.DPR),
                    "file": None,
                },
            },
            files={"0": pdf_upload()},
            map={"0": ["variables.data.file"]},
        )
        assert "errors" in content
        assert not PmerReport.objects.filter(title="No Report Type").exists()

    def test_update_pmer_report(self):
        self.force_login(self.user)
        report = PmerReportFactory.create(
            title="Old Title",
            category=PmerReport.Category.DPR,
            department="Old Department",
            project="Old Project",
            region=None,
            visibility=PmerReport.Visibility.PUBLIC,
            created_by=self.user,
        )
        content = self.query_check(
            self.Mutation.UPDATE_PMER_REPORT,
            variables={
                "id": str(report.pk),
                "data": {
                    "title": "New Title",
                    "category": self.genum(PmerReport.Category.VOLUNTEER_SERVICE_MEMBERSHIP),
                    "reportType": self.genum(PmerReport.DocumentType.STRATEGIC_PLAN),
                    "department": "Volunteer Service",
                    "project": "Membership Drive",
                    "region": str(self.region.pk),
                    "visibility": self.genum(PmerReport.Visibility.PRIVATE),
                },
            },
        )
        resp = content["data"]["updatePmerReport"]
        assert resp["ok"] is True, resp
        assert resp["result"]["title"] == "New Title"
        assert resp["result"]["category"] == self.genum(PmerReport.Category.VOLUNTEER_SERVICE_MEMBERSHIP)
        assert resp["result"]["reportType"] == self.genum(PmerReport.DocumentType.STRATEGIC_PLAN)
        assert resp["result"]["visibility"] == self.genum(PmerReport.Visibility.PRIVATE)
        assert resp["result"]["department"] == "Volunteer Service"
        assert resp["result"]["project"] == "Membership Drive"
        assert resp["result"]["region"] == {"id": str(self.region.pk), "name": "Amhara"}

        report.refresh_from_db()
        assert report.title == "New Title"
        assert report.category == PmerReport.Category.VOLUNTEER_SERVICE_MEMBERSHIP
        assert report.report_type == PmerReport.DocumentType.STRATEGIC_PLAN
        assert report.visibility == PmerReport.Visibility.PRIVATE
        assert report.department == "Volunteer Service"
        assert report.project == "Membership Drive"
        assert report.region == self.region

    def test_update_pmer_report_is_partial(self):
        """Fields left out of the update input keep their existing values."""
        self.force_login(self.user)
        report = PmerReportFactory.create(
            title="Keep Title",
            category=PmerReport.Category.DRR,
            report_type=PmerReport.DocumentType.ANNUAL_PLAN,
            department="Keep Department",
            project="Keep Project",
            region=self.region,
            visibility=PmerReport.Visibility.PRIVATE,
            created_by=self.user,
        )
        content = self.query_check(
            self.Mutation.UPDATE_PMER_REPORT,
            variables={"id": str(report.pk), "data": {"department": "Changed Department"}},
        )
        resp = content["data"]["updatePmerReport"]
        assert resp["ok"] is True, resp
        assert resp["result"]["title"] == "Keep Title"
        assert resp["result"]["category"] == self.genum(PmerReport.Category.DRR)
        assert resp["result"]["reportType"] == self.genum(PmerReport.DocumentType.ANNUAL_PLAN)
        assert resp["result"]["visibility"] == self.genum(PmerReport.Visibility.PRIVATE)
        assert resp["result"]["department"] == "Changed Department"
        assert resp["result"]["project"] == "Keep Project"
        assert resp["result"]["region"] == {"id": str(self.region.pk), "name": "Amhara"}

    def test_update_pmer_report_requires_auth(self):
        self.logout()
        report = PmerReportFactory.create(title="Untouched", created_by=self.user)
        content = self.query_check(
            self.Mutation.UPDATE_PMER_REPORT,
            variables={"id": str(report.pk), "data": {"title": "Hacked"}},
        )
        self.assert_permission_denied(content, "updatePmerReport")
        report.refresh_from_db()
        assert report.title == "Untouched"

    def test_delete_pmer_report(self):
        self.force_login(self.user)
        report = PmerReportFactory.create(created_by=self.user)
        content = self.query_check(
            self.Mutation.DELETE_PMER_REPORT,
            variables={"id": str(report.pk)},
        )
        resp = content["data"]["deletePmerReport"]
        assert resp["ok"] is True, resp
        assert not PmerReport.objects.filter(pk=report.pk).exists()

    def test_delete_pmer_report_requires_auth(self):
        self.logout()
        report = PmerReportFactory.create(created_by=self.user)
        content = self.query_check(
            self.Mutation.DELETE_PMER_REPORT,
            variables={"id": str(report.pk)},
        )
        self.assert_permission_denied(content, "deletePmerReport")
        assert PmerReport.objects.filter(pk=report.pk).exists()

    def test_deleting_missing_pmer_report_is_reported_on_the_payload(self):
        self.force_login(self.user)
        report = PmerReportFactory.create(created_by=self.user)
        report_id = str(report.pk)
        report.delete()
        content = self.query_check(
            self.Mutation.DELETE_PMER_REPORT,
            variables={"id": report_id},
        )
        resp = content["data"]["deletePmerReport"]
        assert resp["ok"] is False, resp
        assert resp["errors"][0]["messages"] == "This PMER Report no longer exists. It may already have been deleted."
