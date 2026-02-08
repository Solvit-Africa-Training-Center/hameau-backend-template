from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from programs.models.internships_models import (
    InternshipApplication,
    Department,
    Supervisor,
    InternshipProgram,
    InternshipFeedback,
)
from programs.serializers.internships_serializers import (
    InternshipApplicationSerializer,
    DepartmentSerializer,
    SupervisorSerializer,
    InternshipProgramSerializer,
    InternshipFeedbackSerializer,
)
from programs.permissions import IsInternshipManager

class InternshipApplicationViewSet(viewsets.ModelViewSet):
    queryset = InternshipApplication.objects.all()
    serializer_class = InternshipApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsInternshipManager]

    @action(detail=True, methods=['post'], url_path='approve-and-assign')
    def approve_and_assign(self, request, pk=None):
        """
        Approve an application and create/update its internship program assignment.
        """
        application = self.get_object()
        
        # 1. Update Application status
        application.status = InternshipApplication.ACCEPTED
        application.reviewed_on = timezone.now()
        application.reviewed_by = request.user
        application.save()

        # 2. Create or Update InternshipProgram
        # Expected data: department, supervisor, start_date, end_date
        assignment_data = request.data.copy()
        assignment_data['application'] = application.id
        assignment_data['status'] = InternshipProgram.ACTIVE

        # Try to find existing program or create new
        try:
            program = InternshipProgram.objects.get(application=application)
            serializer = InternshipProgramSerializer(program, data=assignment_data, partial=True)
        except InternshipProgram.DoesNotExist:
            serializer = InternshipProgramSerializer(data=assignment_data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Application approved and internship assigned successfully.",
                "application_status": application.status,
                "program": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class SupervisorViewSet(viewsets.ModelViewSet):
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer
    permission_classes = [permissions.IsAuthenticated]

class InternshipProgramViewSet(viewsets.ModelViewSet):
    queryset = InternshipProgram.objects.all()
    serializer_class = InternshipProgramSerializer
    permission_classes = [permissions.IsAuthenticated, IsInternshipManager]

class InternshipFeedbackViewSet(viewsets.ModelViewSet):
    queryset = InternshipFeedback.objects.all()
    serializer_class = InternshipFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)
