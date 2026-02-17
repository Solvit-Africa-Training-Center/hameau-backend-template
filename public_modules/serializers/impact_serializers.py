from rest_framework import serializers
from ..models.impact_models import ContactMessage, ImpactStatistic, ContactInfo


class ImpactStatisticSerializer(serializers.ModelSerializer):
  

    class Meta:
        model = ImpactStatistic
        fields = ["id", "title", "value", "description", "order", "is_active", "created_on", "updated_on"]
        read_only_fields = ["id", "created_on", "updated_on"]


class ContactInfoSerializer(serializers.ModelSerializer):
   

    class Meta:
        model = ContactInfo
        fields = ["id", "email", "phone", "address", "is_active", "created_on", "updated_on"]
        read_only_fields = ["id", "created_on", "updated_on"]


class ContactMessageSerializer(serializers.ModelSerializer):
   
    fullname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "first_name",
            "last_name",
            "fullname",
            "email",
            "phone",
            "subject",
            "message",
            "status",
            "admin_notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "fullname", "status", "admin_notes", "created_on", "updated_on"]

    def get_fullname(self, obj):
       
        return obj.fullname


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = ContactMessage
        fields = ["first_name", "last_name", "email", "phone", "subject", "message"]

    def create(self, validated_data):
       
        return ContactMessage.objects.create(
            status=ContactMessage.PENDING, **validated_data
        )


class ContactMessageAdminSerializer(serializers.ModelSerializer):
  
    fullname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "first_name",
            "last_name",
            "fullname",
            "email",
            "phone",
            "subject",
            "message",
            "status",
            "admin_notes",
            "created_on",
            "updated_on",
        ]

    def get_fullname(self, obj):
        
        return obj.fullname
