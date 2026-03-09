from rest_framework import serializers

from website_content.models import Testimonial


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ["id", "name", "image","description", "created_at", "updated_at"]
