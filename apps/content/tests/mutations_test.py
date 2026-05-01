import typing

from apps.content.factories import NewsPostFactory
from apps.content.models import NewsPost
from apps.reports.factories import ReportFactory
from apps.reports.models import Report
from apps.users.factories import UserFactory
from apps.users.models import User
from main.tests import TestCase


class TestNewsPostMutations(TestCase):
    class Mutation:
        CREATE_NEWS_POST = """
            mutation CreateNewsPost($data: NewsPostCreateInput!) {
                createNewsPost(data: $data) {
                    ... on NewsPostTypeMutationResponseType{
                    ok
                    errors
                    result {
                        id
                        title
                        isPublished
                        publishedAt
                    }
                }
            }
        }
        """

        CREATE_NEWS_POST_REPORT = """
            mutation CreateNewsPostReport($data: NewsPostReportInput!) {
                createNewsPostReport(data: $data) {
                    ... on NewsPostReportTypeMutationResponseType{
                        errors
                        ok
                    result {
                        id
                        order
                    }
                }
            }
        }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.staff_user = UserFactory.create(role=User.Role.STAFF)
        cls.viewer = UserFactory.create(role=User.Role.VIEWER)
        cls.public_report = ReportFactory.create(visibility=Report.Visibility.PUBLIC)
        cls.private_report = ReportFactory.create(visibility=Report.Visibility.PRIVATE)

    def test_create_news_post(self):
        self.force_login(self.staff_user)
        content = self.query_check(
            self.Mutation.CREATE_NEWS_POST,
            variables={"data": {"title": "Breaking News", "content": "**Important** update."}},
        )
        resp = content["data"]["createNewsPost"]
        assert resp["ok"] is True
        assert resp["result"]["title"] == "Breaking News"
        assert resp["result"]["isPublished"] is False
        assert resp["result"]["publishedAt"] is None

    def test_create_and_publish_news_post(self):
        self.force_login(self.staff_user)
        content = self.query_check(
            self.Mutation.CREATE_NEWS_POST,
            variables={"data": {"title": "Live Now", "content": "Content.", "isPublished": True}},
        )
        resp = content["data"]["createNewsPost"]
        assert resp["ok"] is True
        post = NewsPost.objects.get(pk=resp["result"]["id"])
        assert post.published_at is not None

    def test_viewer_cannot_create_post(self):
        self.force_login(self.viewer)
        content = self.query_check(
            self.Mutation.CREATE_NEWS_POST,
            assert_errors=True,
            variables={"data": {"title": "Blocked", "content": "content"}},
        )
        assert "errors" in content

    def test_cannot_link_private_report(self):
        self.force_login(self.staff_user)
        newspost = NewsPostFactory.create(author=self.staff_user)
        content = self.query_check(
            self.Mutation.CREATE_NEWS_POST_REPORT,
            variables={"data": {"newspost": str(newspost.pk), "report": str(self.private_report.pk), "order": 0}},
        )
        resp = content["data"]["createNewsPostReport"]
        assert resp["ok"] is False
        assert resp["errors"] is not None
