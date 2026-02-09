from rest_framework import serializers
from django.utils import timezone
# from utils.emails import send_internship_status_email
from programs.tasks import send_status_email_task
from programs.models.internships_models import (
    InternshipApplication,
    Department,
    Supervisor,
    InternshipProgram
)
from django.db import transaction


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description", "created_on", "updated_on"]
        read_only_fields = ["id", "created_on", "updated_on"]
        
class SupervisorSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source="department.name")

    class Meta:
        model = Supervisor
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "department_name",
            "is_active",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "department_name", "created_on", "updated_on"]


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
            "date_of_birth",
            "nationality",
            "is_in_rwanda",
            "school_university",
            "field_of_study",
            "cv_url",
            "motivation_letter",
            "status",
            "status_display",
            "admin_notes",
            "applied_on",
            "reviewed_on",
            "reviewed_by",
        ]
        read_only_fields = [
            "id",
            "full_name",
            "applied_on",
            "reviewed_on",
            "reviewed_by",
            "status_display",
        ]

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get("status", old_status)

        if old_status != new_status:
            instance.reviewed_on = timezone.now()
            request = self.context.get("request")
            if request and getattr(request, "user", None):
                instance.reviewed_by = request.user

        instance = super().update(instance, validated_data)

        if old_status != new_status:
            try:
                send_status_email_task.delay_on_commit(instance.id)
            except Exception as e:
                print(f"Error sending email: {e}")

        return instance

class InternshipProgramSerializer(serializers.ModelSerializer):
    application_name = serializers.ReadOnlyField(source="application.full_name")
    department_name = serializers.ReadOnlyField(source="department.name")
    supervisor_name = serializers.ReadOnlyField(source="supervisor.full_name")

    class Meta:
        model = InternshipProgram
        fields = [
            "id",
            "application",
            "application_name",
            "department",
            "department_name",
            "supervisor",
            "supervisor_name",
            "start_date",
            "end_date",
            "status",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "application_name", "department_name", "supervisor_name", "created_on", "updated_on"]

    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        supervisor = data.get("supervisor")
        department = data.get("department")
        application = data.get("application")
        status_value = data.get("status")

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({"end_date": "End date must be after start date."})

        if supervisor and department and getattr(supervisor, "department", None) != department:
            raise serializers.ValidationError({
                "supervisor": "The assigned supervisor must belong to the selected department."
            })

        if not self.instance and application is not None:
            if getattr(application, "internship_program", None) is not None:
                raise serializers.ValidationError({
                    "application": "Application already has an internship program"
                })

      
        if status_value is not None:
            valid_statuses = [InternshipProgram.ACTIVE, InternshipProgram.COMPLETED, InternshipProgram.TERMINATED]
            if status_value not in valid_statuses:
                raise serializers.ValidationError({
                    "status": "Invalid status. Must be ACTIVE, COMPLETED, or TERMINATED."
                })

           
            if self.instance and status_value in [InternshipProgram.COMPLETED, InternshipProgram.TERMINATED]:
                if self.instance.status != InternshipProgram.ACTIVE:
                    raise serializers.ValidationError({
                        "status": "Only active programs can be ended."
                    })

        return data

    def create(self, validated_data):
        application = validated_data.get("application")

        
        validated_data["status"] = InternshipProgram.ACTIVE

        with transaction.atomic():
            program = InternshipProgram.objects.create(**validated_data)

            
            if application is not None:
                application.status = InternshipApplication.ACCEPTED
                application.reviewed_on = timezone.now()
                request = self.context.get("request")
                if request and getattr(request, "user", None):
                    application.reviewed_by = request.user
                application.save()

                try:
                    send_status_email_task.delay_on_commit(application.id)
                except Exception as e:
                    raise serializers.ValidationError("Fail to send the email:  application status",e)

        return program



        
