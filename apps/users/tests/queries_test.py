import typing

from apps.users.factories import UserFactory
from apps.users.models import User
from main.tests import TestCase


class TestUserQueries(TestCase):
    class Query:
        ME = """
            query Me {
                me {
                    id
                    email
                    fullName
                    role
                    isActive
                    mfaEnabled
                    createdAt
                }
            }
        """

    @typing.override
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create(
            email="test@ercs.org",
            full_name="Test User",
            role=User.Role.STAFF,
        )

    def test_me_unauthenticated(self):
        self.logout()
        content = self.query_check(self.Query.ME)
        assert content["data"]["me"] is None

    def test_me_authenticated(self):
        self.force_login(self.user)
        content = self.query_check(self.Query.ME)
        me = content["data"]["me"]
        assert me["email"] == "test@ercs.org"
        assert me["fullName"] == "Test User"
        assert me["role"] == User.Role.STAFF
        assert me["isActive"] is True
