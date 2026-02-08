from rest_framework import serializers
<<<<<<< HEAD
from programs.models.internships_models import (
    InternshipApplication,
    Department,
    Supervisor,
    InternshipProgram,
    InternshipFeedback,
)

class InternshipApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternshipApplication
        fields = "__all__"
        read_only_fields = ("id", "applied_on", "reviewed_on", "reviewed_by")

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = ("id",)

class SupervisorSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source="department.name")

    class Meta:
        model = Supervisor
        fields = "__all__"
        read_only_fields = ("id",)

class InternshipProgramSerializer(serializers.ModelSerializer):
    application_name = serializers.ReadOnlyField(source="application.full_name")
    department_name = serializers.ReadOnlyField(source="department.name")
    supervisor_name = serializers.ReadOnlyField(source="supervisor.full_name") #

    class Meta:
        model = InternshipProgram
        fields = "__all__"
        read_only_fields = ("id",)

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        supervisor = data.get('supervisor')
        department = data.get('department')

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({
                "end_date": "End date must be after start date."
            })
        
        # Ensure supervisor belongs to the selected department
        if supervisor and department and supervisor.department != department:
            raise serializers.ValidationError({
                "supervisor": "The assigned supervisor must belong to the selected department."
            })

        return data

class InternshipFeedbackSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.ReadOnlyField(source="submitted_by.full_name")

    class Meta:
        model = InternshipFeedback
        fields = "__all__"
        read_only_fields = ("id", "submitted_on", "submitted_by")
=======
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
>>>>>>> e5007aa329cde90bb4138dd96c1d4ef871f9a328
