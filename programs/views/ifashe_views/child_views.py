import logging
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

logger = logging.getLogger(__name__)


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

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} registered a new child: {instance.full_name} (ID: {instance.id})"
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} updated child: {instance.full_name} (ID: {instance.id})"
        )

    def perform_destroy(self, instance):
        name = instance.full_name
        c_id = instance.id
        instance.delete()
        logger.warning(
            f"User {self.request.user} removed child: {name} (ID: {c_id})"
        )

@extend_schema(
    tags=["IfasheTugufashe - Family "],
)
class DressingDistributionViewSet(viewsets.ModelViewSet):
    queryset = DressingDistribution.objects.select_related("child")
    serializer_class = DressingDistributionSerializer
    permission_classes = [IsIfasheManager]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} recorded dressing distribution ({instance.item_type}) for child {instance.child} (ID: {instance.id})"
        )
