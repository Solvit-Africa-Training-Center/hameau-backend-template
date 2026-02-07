from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from ...models.internships_models import InternshipApplication
from ...serializers.internships_serializers import InternshipApplicationSerializer
from utils.paginators import StandardResultsSetPagination

class InternshipApplicationViewSet(viewsets.ModelViewSet):
    queryset = InternshipApplication.objects.all().order_by("-applied_on")
    serializer_class = InternshipApplicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["country", "education_level", "status"]
    search_fields = ["first_name", "last_name", "email", "phone", "school_university"]
    ordering_fields = ["applied_on", "status"]

    def perform_create(self, serializer):
        # Additional logic if needed when creating
        serializer.save()
