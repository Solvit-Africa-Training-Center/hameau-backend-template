from rest_framework import serializers
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
