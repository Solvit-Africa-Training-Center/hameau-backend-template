from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema 
from accounts.permissions import IsInternshipManager
from rest_framework.permissions import AllowAny
from utils.paginators import StandardResultsSetPagination

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
    InternshipAssignmentSerializer,
    InternshipProgramSerializer,
    InternshipFeedbackSerializer,
)

@extend_schema(tags=["Internship - Applications"])
class InternshipApplicationViewSet(viewsets.ModelViewSet):
    queryset = InternshipApplication.objects.all().order_by("-applied_on")
    serializer_class = InternshipApplicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["country", "education_level", "status"]
    search_fields = ["first_name", "last_name", "email", "phone", "school_university"]
    ordering_fields = ["applied_on", "status"]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [permissions.IsAuthenticated(), IsInternshipManager()]

    @extend_schema(request=InternshipAssignmentSerializer, responses={200: InternshipApplicationSerializer})
    @action(detail=True, methods=['post'], url_path='approve-and-assign')
    def approve_and_assign(self, request, pk=None):
        """
        Approve an application and create/update its internship program assignment.
        """
        application = self.get_object()
        serializer = InternshipAssignmentSerializer(application, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(InternshipApplicationSerializer(application).data, status=status.HTTP_200_OK)

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
