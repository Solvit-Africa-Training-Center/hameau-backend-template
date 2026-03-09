from rest_framework import serializers

from website_content.models import Team


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "full_name", "position", "image", "linkedin_url", "created_at", "updated_at"]
    
    