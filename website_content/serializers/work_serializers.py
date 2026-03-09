from rest_framework import serializers

from website_content.models import Work

class WorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Work
        fields = ["id", "title", "description"]
    