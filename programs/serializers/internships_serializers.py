from rest_framework import serializers
from programs.models.internships_models import (
    InternshipApplication,
    Department,
    Supervisor,
    InternshipProgram,
    InternshipFeedback,
)



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
    supervisor_name = serializers.ReadOnlyField(source="supervisor.full_name") ###########

    class Meta:
        model = InternshipProgram
        fields = "__all__"
        read_only_fields = ("id",)

         #i have updated the validation starting date is 
         # before the end date and the supervisor belongs to the selected department

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


class InternshipAssignmentSerializer(serializers.Serializer):
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    supervisor = serializers.PrimaryKeyRelatedField(queryset=Supervisor.objects.all())
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        supervisor = data.get('supervisor')
        department = data.get('department')

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({
                "end_date": "End date must be after start date."
            })
        
        if supervisor and department and supervisor.department != department:
            raise serializers.ValidationError({
                "supervisor": "The assigned supervisor must belong to the selected department."
            })
            
        return data

    def create(self, validated_data):
        # We are "creating" an assignment, but effectively updating the application and creating/updating the program
        # ideally this is called via serializer.save() which calls create or update depending on if instance is passed.
        # But we are using a Serializer, not ModelSerializer, so we define how it behaves.
        # Actually, it's better to pass the application as 'instance' to the serializer and use update().
        pass

    def update(self, instance, validated_data):
        # instance is InternshipApplication
        from django.utils import timezone
        
        # 1. Update Application status
        instance.status = InternshipApplication.APPROVED
        instance.reviewed_on = timezone.now()
        instance.reviewed_by = self.context['request'].user
        instance.save()

        # 2. Create or Update InternshipProgram
        InternshipProgram.objects.update_or_create(
            application=instance,
            defaults={
                'department': validated_data['department'],
                'supervisor': validated_data['supervisor'],
                'start_date': validated_data['start_date'],
                'end_date': validated_data['end_date'],
                'status': InternshipProgram.ACTIVE
            }
        )
        
        # Send email notification
        try:
            send_internship_status_email(instance)
        except Exception as e:
            print(f"Error sending email: {e}")

        return instance

