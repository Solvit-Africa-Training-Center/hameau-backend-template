from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema 
from accounts.permissions import IsInternshipManager
from rest_framework.permissions import AllowAny
from ...models.internships_models import InternshipApplication
from ...serializers.internships_serializers import InternshipApplicationSerializer
from utils.paginators import StandardResultsSetPagination

@extend_schema(
    tags=["Internship - Applications"],
)
class InternshipApplicationViewSet(viewsets.ModelViewSet):
    queryset = InternshipApplication.objects.all().order_by("-applied_on")
    serializer_class = InternshipApplicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["nationality", "is_in_rwanda", "status"]
    search_fields = ["first_name", "last_name", "email", "phone", "school_university", "field_of_study"]
    ordering_fields = ["applied_on", "status"]

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated(), IsInternshipManager()]
