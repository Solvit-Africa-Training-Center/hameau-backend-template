from rest_framework import serializers

from website_content.models import WeAre    

class WeAreSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeAre
        fields = ["id", "title", "description"]

    