from rest_framework import serializers

from public_modules.models import TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = [
            "id",
            "name",
            "job_title",
            "image",
        ]
