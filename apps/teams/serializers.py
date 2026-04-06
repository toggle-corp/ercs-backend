from rest_framework import serializers

from .models import Team, TeamMember


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "description"]


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = ["team", "name", "position", "email", "phone_number", "order"]
