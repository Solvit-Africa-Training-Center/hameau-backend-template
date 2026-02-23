from rest_framework import serializers

from public_modules.models import ContactMessage
from utils.emails import send_contact_message_email


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "name",
            "email",
            "phone_number",
            "message",
            "created_on",
        ]
        read_only_fields = ["id", "created_on"]

    def create(self, validated_data):
        contact_message = ContactMessage.objects.create(**validated_data)
        send_contact_message_email(contact_message)
        return contact_message
