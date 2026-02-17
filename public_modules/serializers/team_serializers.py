from rest_framework import serializers
from ..models.team_models import TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
   

    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TeamMember
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "role",
            #"bio",
            "photo",
            "order",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "full_name", "created_on", "updated_on"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()