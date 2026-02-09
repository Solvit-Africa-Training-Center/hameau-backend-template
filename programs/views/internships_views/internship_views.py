from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from accounts.permissions import IsInternshipManager
from ...models.internships_models import InternshipProgram, InternshipApplication, Supervisor
from ...serializers.internships_serializers import InternshipProgramSerializer
from utils.paginators import StandardResultsSetPagination
from django.utils import timezone
from utils.emails import send_internship_status_email
from django.db import transaction
from datetime import datetime

@extend_schema(
    tags=["Internship - Programs"],
)
class InternshipProgramViewSet(viewsets.ModelViewSet):
    queryset = InternshipProgram.objects.all().select_related("application", "department", "supervisor").order_by("-start_date")
    serializer_class = InternshipProgramSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsInternshipManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "department", "supervisor"]
    search_fields = ["application__first_name", "application__last_name", "application__email"]
    ordering_fields = ["start_date", "end_date", "status"]
    
    @action(detail=False, methods=["post"])
    def add_applicant(self, request):
        application_id = request.data.get("application_id")
        department_id = request.data.get("department")
        supervisor_id = request.data.get("supervisor")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        if not all([application_id, department_id, supervisor_id, start_date, end_date]):
            return Response(
                {"error": "Missing required fields: application_id, department, supervisor, start_date, end_date"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            application = InternshipApplication.objects.get(id=application_id)
        except InternshipApplication.DoesNotExist:
            return Response(
                {"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if hasattr(application, "internship_program"):
            return Response(
                {"error": "Application already has an internship program"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            supervisor = Supervisor.objects.get(id=supervisor_id)
        except Supervisor.DoesNotExist:
            return Response(
                {"error": "Supervisor not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if str(supervisor.department_id) != str(department_id):
            return Response(
                {"error": "The assigned supervisor must belong to the selected department."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate dates
        try:
            start = datetime.strptime(str(start_date), "%Y-%m-%d").date() if isinstance(start_date, str) else start_date
            end = datetime.strptime(str(end_date), "%Y-%m-%d").date() if isinstance(end_date, str) else end_date
            
            if start >= end:
                return Response(
                    {"error": "End date must be after start date."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except (ValueError, AttributeError):
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            program = InternshipProgram.objects.create(
                application=application,
                department_id=department_id,
                supervisor_id=supervisor_id,
                start_date=start_date,
                end_date=end_date,
                status=InternshipProgram.ACTIVE,
            )

            application.status = InternshipApplication.ACCEPTED
            application.reviewed_on = timezone.now()
            application.reviewed_by = request.user
            application.save()

            try:
                send_internship_status_email(application)
            except Exception as e:
                print(f"Error sending email: {e}")

        serializer = self.get_serializer(program)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"])
    def update_program(self, request, pk=None):
        program = self.get_object()
        serializer = self.get_serializer(program, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def end_program(self, request, pk=None):
        program = self.get_object()
        
        if program.status != InternshipProgram.ACTIVE:
             return Response(
                {"error": "Only active programs can be ended."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        program_status = request.data.get("status", InternshipProgram.COMPLETED)
        end_date = request.data.get("end_date") 

        if program_status not in [InternshipProgram.COMPLETED, InternshipProgram.TERMINATED]:
             return Response(
                {"error": "Invalid status. Must be COMPLETED or TERMINATED."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        program.status = program_status
        if end_date:
            program.end_date = end_date
            
        program.save()

        serializer = self.get_serializer(program)
        return Response(serializer.data)
    
    