from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from accounts.permissions import IsInternshipManager
from ...models.internships_models import InternshipProgram
from ...serializers.internships_serializers import InternshipProgramSerializer
from utils.paginators import StandardResultsSetPagination

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
        data = {
            "application": request.data.get("application_id") or request.data.get("application"),
            "department": request.data.get("department"),
            "supervisor": request.data.get("supervisor"),
            "start_date": request.data.get("start_date"),
            "end_date": request.data.get("end_date"),
        }

        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        program = serializer.save()

        return Response(self.get_serializer(program).data, status=status.HTTP_201_CREATED)
    
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
        serializer = self.get_serializer(program, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    