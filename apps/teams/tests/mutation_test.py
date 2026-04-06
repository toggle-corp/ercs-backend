import typing

from apps.users.factories import UserFactory
from apps.users.models import User
from main.tests import TestCase


class TestTeamMutations(TestCase):
    class Mutation:
        CREATE_TEAM = """
            mutation CreateTeam($data: TeamCreateInput!) {
                createTeam(data: $data) {
                    ok
                    errors
                    result {
                        id
                        name
                        teamType
                    }
                }
            }
        """

        UPDATE_TEAM = """
            mutation UpdateTeam($id: ID!, $data: TeamUpdateInput!) {
                updateTeam(id: $id, data: $data) {
                    ok
                    errors
                    result {
                        id
                        name
                        teamType
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

    def test_create_team(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.CREATE_TEAM,
            variables={"data": {"name": "Rapid Response", "teamType": "BDRT"}},
        )
        resp = content["data"]["createTeam"]
        assert resp["ok"] is True
        assert resp["result"]["name"] == "Rapid Response"
        assert resp["result"]["teamType"] == "BDRT"

    def test_viewer_cannot_create_team(self):
        self.force_login(self.viewer)
        content = self.query_check(
            self.Mutation.CREATE_TEAM,
            assert_errors=True,
            variables={"data": {"name": "Blocked", "teamType": "CBHFA"}},
        )
        assert "errors" in content

    def test_update_team(self):
        self.force_login(self.staff)
        # First create
        create_content = self.query_check(
            self.Mutation.CREATE_TEAM,
            variables={"data": {"name": "Old Name", "teamType": "BDRT"}},
        )
        team_id = create_content["data"]["createTeam"]["result"]["id"]

        # Then update
        content = self.query_check(
            self.Mutation.UPDATE_TEAM,
            variables={"id": team_id, "data": {"name": "New Name"}},
        )
        resp = content["data"]["updateTeam"]
        assert resp["ok"] is True
        assert resp["result"]["name"] == "New Name"
        assert resp["result"]["teamType"] == "BDRT"
