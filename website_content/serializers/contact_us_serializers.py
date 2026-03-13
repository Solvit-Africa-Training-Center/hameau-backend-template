from rest_framework import serializers

from website_content.models import ContactMessage, ReplyToContactMessage

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "first_name", "last_name", "email", "phone_number", "message", "is_read", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

  
            
    

class ReplyToContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplyToContactMessage
        fields = ["id", "contact_message", "reply", "created_at", "updated_at"] 
        read_only_fields = ["created_at","updated_at"]
