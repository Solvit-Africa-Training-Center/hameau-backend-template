import logging
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import Family
from programs.serializers.ifashe_serializers import IfasheFamilySerializer

from accounts.permissions import IsIfasheManager
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


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

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} created a new family: {instance.family_name} (ID: {instance.id})"
        )

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_vulnerability = old_instance.vulnerability_level
        instance = serializer.save()
        
        log_msg = f"User {self.request.user} updated family: {instance.family_name} (ID: {instance.id})"
        if old_vulnerability != instance.vulnerability_level:
            log_msg += f" | Vulnerability changed from {old_vulnerability} to {instance.vulnerability_level}"
        
        logger.info(log_msg)

    def perform_destroy(self, instance):
        family_name = instance.family_name
        family_id = instance.id
        instance.delete()
        logger.warning(
            f"User {self.request.user} deleted family: {family_name} (ID: {family_id})"
        )
