from rest_framework import serializers

from public_modules.models import ContactMessage
from public_modules.tasks import send_contact_message_email_task


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
        send_contact_message_email_task.delay(str(contact_message.id))
        return contact_message
