from rest_framework import serializers

from website_content.models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "first_name", "last_name", "email", "phone_number", "message", "created_at", "updated_at"]
    

    