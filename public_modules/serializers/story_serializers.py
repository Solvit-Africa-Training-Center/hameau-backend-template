from rest_framework import serializers

from public_modules.models import SuccessStory


class SuccessStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessStory
        fields = [
            "id",
            "image",
            "title",
            "body",
            "location",
        ]
