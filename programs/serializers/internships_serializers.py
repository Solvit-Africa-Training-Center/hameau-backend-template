from rest_framework import serializers
from ..models.internships_models import InternshipApplication
from utils.emails import send_internship_status_email

class InternshipApplicationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = InternshipApplication
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "phone",
            "country",
            "education_level",
            "program",
            "availability_hours",
            "date_of_birth",
            "nationality",
            "is_in_rwanda",
            "school_university",
            "field_of_study",
            "cv_url",
            "motivation_letter",
            "passport_id_url",
            "status",
            "status_display",
            "admin_notes",
            "applied_on",
            "reviewed_on",
            "reviewed_by",
        ]
        read_only_fields = ["id", "applied_on", "reviewed_on", "reviewed_by"]

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get("status", old_status)

        # Logic: If status changed, update review metadata
        if old_status != new_status:
            from django.utils import timezone
            instance.reviewed_on = timezone.now()
            
            request = self.context.get("request")
            if request and request.user:
                instance.reviewed_by = request.user

        # Update the instance
        instance = super().update(instance, validated_data)

        # Logic: If status changed, send email notification
        if old_status != new_status:
            try:
                send_internship_status_email(instance)
            except Exception as e:
                # Log error but don't fail the update
                print(f"Error sending email: {e}")

        return instance
