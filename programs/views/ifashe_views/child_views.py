from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import SponsoredChild
from programs.models.ifashe_models import DressingDistribution
from programs.serializers.ifashe_serializers import (
    DressingDistributionSerializer,
    IfasheChildSerializer,
)


from accounts.permissions import IsIfasheManager
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["IfasheTugufashe - Family "],
)
class IfasheChildViewSet(viewsets.ModelViewSet):
    queryset = SponsoredChild.objects.all().select_related("family")
    serializer_class = IfasheChildSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["school_name", "school_level", "support_status", "gender"]
    search_fields = ["first_name", "last_name", "family__family_name"]
    ordering_fields = ["created_on", "first_name", "last_name", "date_of_birth"]
    ordering = ["-created_on"]

@extend_schema(
    tags=["IfasheTugufashe - Family "],
)
class DressingDistributionViewSet(viewsets.ModelViewSet):
    queryset = DressingDistribution.objects.select_related("child")
    serializer_class = DressingDistributionSerializer
    permission_classes = [IsIfasheManager]
