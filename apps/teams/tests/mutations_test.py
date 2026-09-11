import typing

from apps.geo.factories import RegionFactory
from apps.teams.factories import TeamFactory
from apps.teams.models import Team, TeamMember
from apps.users.factories import UserFactory
from apps.users.models import User
from main.tests import TestCase


class TestTeamMutations(TestCase):
    class Mutation:
        CREATE_TEAM = """
            mutation CreateTeam($data: TeamCreateInput!) {
                createTeam(data: $data) {
                    ... on TeamTypeMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            name
                        }
                    }
                }
            }
        """

        UPDATE_TEAM = """
            mutation UpdateTeam($id: ID!, $data: TeamUpdateInput!) {
                updateTeam(id: $id, data: $data) {
                    ... on TeamTypeMutationResponseType{


                    ok
                    errors
                    result {
                        id
                        name
                    }
                }
            }
        }
        """

        DELETE_TEAM = """
            mutation DeleteTeam($id: ID!) {
                deleteTeam(id: $id) {
                    ok
                    errors
                }
            }
        """

        DELETE_TEAM_MEMBER = """
            mutation DeleteTeamMember($id: ID!) {
                deleteTeamMember(id: $id) {
                    ok
                    errors
                }
            }
        """

        BULK_CREATE_TEAM_MEMBERS = """
            mutation BulkCreateTeamMembers($data: TeamMemberBulkCreateInput!) {
                bulkCreateTeamMembers(data: $data) {
                    ... on TeamMemberTypeListMutationResponseType {
                        ok
                        errors
                        result {
                            id
                            teamId
                            name
                            position
                            email
                            phoneNumber
                            sex
                            region
                            woreda
                            training
                            fieldOfStudy
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
        cls.staff = UserFactory.create(is_staff=True, role=User.Role.STAFF)
        cls.viewer = UserFactory.create(role=User.Role.VIEWER)

    def test_create_team(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.CREATE_TEAM,
            variables={"data": {"name": "Rapid Response"}},
        )
        resp = content["data"]["createTeam"]
        assert resp["ok"] is True
        assert resp["result"]["name"] == "Rapid Response"

    def test_viewer_cannot_create_team(self):
        self.force_login(self.viewer)
        content = self.query_check(
            self.Mutation.CREATE_TEAM,
            variables={"data": {"name": "Blocked"}},
        )
        self.assert_permission_denied(content, "createTeam")

    def test_update_team(self):
        self.force_login(self.staff)
        # First create
        create_content = self.query_check(
            self.Mutation.CREATE_TEAM,
            variables={"data": {"name": "Old Name"}},
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

    def test_bulk_create_team_members_all_fields(self):
        self.force_login(self.staff)
        team = TeamFactory.create()
        region = RegionFactory.create()
        members = [
            {
                "team": self.gID(team.pk),
                "name": f"Member {i}",
                "position": "Volunteer",
                "email": f"member{i}@example.com",
                "phoneNumber": f"+25190000000{i}",
                "sex": self.genum(TeamMember.Sex.FEMALE),
                "region": self.gID(region.pk),
                "training": "First Aid",
                "fieldOfStudy": "Public Health",
                "order": i,
            }
            for i in range(3)
        ]
        content = self.query_check(
            self.Mutation.BULK_CREATE_TEAM_MEMBERS,
            variables={"data": {"members": members}},
        )
        resp = content["data"]["bulkCreateTeamMembers"]
        assert resp["ok"] is True
        assert resp["errors"] is None
        assert len(resp["result"]) == 3
        assert TeamMember.objects.count() == 3
        first = resp["result"][0]
        assert first["name"] == "Member 0"
        assert first["teamId"] == self.gID(team.pk)
        assert first["region"] == self.gID(region.pk)
        assert first["sex"] == self.genum(TeamMember.Sex.FEMALE)

    def test_bulk_create_team_members_minimal_required_fields(self):
        self.force_login(self.staff)
        team = TeamFactory.create()
        region = RegionFactory.create()
        members = [
            {
                "team": self.gID(team.pk),
                "name": "Only Required",
                "position": "Lead",
                "region": self.gID(region.pk),
            },
        ]
        content = self.query_check(
            self.Mutation.BULK_CREATE_TEAM_MEMBERS,
            variables={"data": {"members": members}},
        )
        resp = content["data"]["bulkCreateTeamMembers"]
        assert resp["ok"] is True
        assert len(resp["result"]) == 1
        assert TeamMember.objects.count() == 1
        assert resp["result"][0]["region"] == self.gID(region.pk)

    def test_bulk_create_team_members_without_region_fails(self):
        self.force_login(self.staff)
        team = TeamFactory.create()
        members = [
            # region is required in the schema -> request must fail at validation
            {"team": self.gID(team.pk), "name": "No Region", "position": "Lead"},
        ]
        content = self.query_check(
            self.Mutation.BULK_CREATE_TEAM_MEMBERS,
            assert_errors=True,
            variables={"data": {"members": members}},
        )
        assert "errors" in content
        assert TeamMember.objects.count() == 0

    def test_bulk_create_with_invalid_region_fails(self):
        self.force_login(self.staff)
        team = TeamFactory.create()
        members = [
            {
                "team": self.gID(team.pk),
                "name": "Bad Region",
                "position": "Lead",
                "region": "00000000-0000-0000-0000-000000000000",
            },
        ]
        content = self.query_check(
            self.Mutation.BULK_CREATE_TEAM_MEMBERS,
            variables={"data": {"members": members}},
        )
        resp = content["data"]["bulkCreateTeamMembers"]
        assert resp["ok"] is False
        assert resp["errors"] is not None
        assert TeamMember.objects.count() == 0

    def test_bulk_create_empty_list(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.BULK_CREATE_TEAM_MEMBERS,
            variables={"data": {"members": []}},
        )
        resp = content["data"]["bulkCreateTeamMembers"]
        assert resp["ok"] is True
        assert resp["result"] == []
        assert TeamMember.objects.count() == 0

    def test_bulk_create_is_atomic_when_a_row_is_invalid(self):
        self.force_login(self.staff)
        team = TeamFactory.create()
        region = RegionFactory.create()
        members = [
            {"team": self.gID(team.pk), "name": "Valid", "position": "Lead", "region": self.gID(region.pk)},
            # schema-valid but serializer-invalid (bad email) -> whole batch must fail
            {
                "team": self.gID(team.pk),
                "name": "Invalid",
                "position": "Lead",
                "region": self.gID(region.pk),
                "email": "not-an-email",
            },
        ]
        content = self.query_check(
            self.Mutation.BULK_CREATE_TEAM_MEMBERS,
            variables={"data": {"members": members}},
        )
        resp = content["data"]["bulkCreateTeamMembers"]
        assert resp["ok"] is False
        assert resp["errors"] is not None
        assert resp["result"] is None
        # atomicity: the valid row must NOT have been persisted
        assert TeamMember.objects.count() == 0

    def test_bulk_create_with_invalid_team_fails(self):
        self.force_login(self.staff)
        region = RegionFactory.create()
        members = [
            {
                "team": "00000000-0000-0000-0000-000000000000",
                "name": "Orphan",
                "position": "Lead",
                "region": self.gID(region.pk),
            },
        ]
        content = self.query_check(
            self.Mutation.BULK_CREATE_TEAM_MEMBERS,
            variables={"data": {"members": members}},
        )
        resp = content["data"]["bulkCreateTeamMembers"]
        assert resp["ok"] is False
        assert resp["errors"] is not None
        assert TeamMember.objects.count() == 0

    def test_viewer_cannot_bulk_create_team_members(self):
        self.force_login(self.viewer)
        team = TeamFactory.create()
        region = RegionFactory.create()
        members = [
            {"team": self.gID(team.pk), "name": "Blocked", "position": "Lead", "region": self.gID(region.pk)},
        ]
        content = self.query_check(
            self.Mutation.BULK_CREATE_TEAM_MEMBERS,
            variables={"data": {"members": members}},
        )
        self.assert_permission_denied(content, "bulkCreateTeamMembers")
        assert TeamMember.objects.count() == 0

    def test_staff_can_delete_team(self):
        self.force_login(self.staff)
        team = TeamFactory.create()
        content = self.query_check(
            self.Mutation.DELETE_TEAM,
            variables={"id": str(team.pk)},
        )
        resp = content["data"]["deleteTeam"]
        assert resp["ok"] is True, resp
        assert not Team.objects.filter(pk=team.pk).exists()

    def test_viewer_cannot_delete_team(self):
        self.force_login(self.viewer)
        team = TeamFactory.create()
        content = self.query_check(
            self.Mutation.DELETE_TEAM,
            variables={"id": str(team.pk)},
        )
        self.assert_permission_denied(content, "deleteTeam")
        assert Team.objects.filter(pk=team.pk).exists()

    def test_deleting_missing_team_is_reported_on_the_payload(self):
        self.force_login(self.staff)
        team = TeamFactory.create()
        team_id = str(team.pk)
        team.delete()
        content = self.query_check(
            self.Mutation.DELETE_TEAM,
            variables={"id": team_id},
        )
        resp = content["data"]["deleteTeam"]
        assert resp["ok"] is False, resp
        assert resp["errors"][0]["messages"] == "This Team no longer exists. It may already have been deleted."

    def test_staff_can_delete_team_member(self):
        self.force_login(self.staff)
        team = TeamFactory.create()
        member = TeamMember.objects.create(team=team, name="Gone", position="Lead", region=RegionFactory.create())
        content = self.query_check(
            self.Mutation.DELETE_TEAM_MEMBER,
            variables={"id": str(member.pk)},
        )
        resp = content["data"]["deleteTeamMember"]
        assert resp["ok"] is True, resp
        assert not TeamMember.objects.filter(pk=member.pk).exists()

    def test_viewer_cannot_delete_team_member(self):
        self.force_login(self.viewer)
        team = TeamFactory.create()
        member = TeamMember.objects.create(team=team, name="Stays", position="Lead", region=RegionFactory.create())
        content = self.query_check(
            self.Mutation.DELETE_TEAM_MEMBER,
            variables={"id": str(member.pk)},
        )
        self.assert_permission_denied(content, "deleteTeamMember")
        assert TeamMember.objects.filter(pk=member.pk).exists()

    def test_deleting_team_cascades_to_members(self):
        self.force_login(self.staff)
        team = TeamFactory.create()
        TeamMember.objects.create(team=team, name="Member", position="Lead", region=RegionFactory.create())
        content = self.query_check(
            self.Mutation.DELETE_TEAM,
            variables={"id": str(team.pk)},
        )
        resp = content["data"]["deleteTeam"]
        assert resp["ok"] is True, resp
        assert not TeamMember.objects.filter(team_id=team.pk).exists()

    def test_deleting_with_a_malformed_id_is_reported_on_the_payload(self):
        self.force_login(self.staff)
        content = self.query_check(
            self.Mutation.DELETE_TEAM,
            variables={"id": ""},
        )
        resp = content["data"]["deleteTeam"]
        assert resp["ok"] is False, resp
        assert resp["errors"][0]["messages"] == "This Team no longer exists. It may already have been deleted."
