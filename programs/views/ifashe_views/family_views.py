from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import Family
from programs.serializers.ifashe_serializers import IfasheFamilySerializer

from accounts.permissions import IsIfasheManager
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["IfasheTugufashe - Family "],
)
class IfasheFamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all().prefetch_related("parents", "children")
    serializer_class = IfasheFamilySerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "province",
        "district",
        "sector",
        "vulnerability_level",
        "housing_condition",
    ]
    search_fields = ["family_name", "address"]
    ordering_fields = ["created_on", "family_name", "vulnerability_level"]
    ordering = ["-created_on"]
