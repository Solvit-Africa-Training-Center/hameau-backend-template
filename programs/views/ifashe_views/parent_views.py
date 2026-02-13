import logging
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import Parent
from programs.models.ifashe_models import (
    ParentAttendance,
    ParentPerformance,
    ParentWorkContract,
)
from programs.serializers.ifashe_serializers import (
    IfasheParentSerializer,
    ParentAttendanceSerializer,
    ParentPerformanceSerializer,
    ParentWorkContractSerializer,
)
from accounts.permissions import IsIfasheManager
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["IfasheTugufashe - Family "],
)
class IfasheParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all().select_related("family")
    serializer_class = IfasheParentSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["gender", "relationship", "marital_status"]
    search_fields = ["first_name", "last_name", "national_id", "phone"]
    ordering_fields = ["created_on", "first_name", "last_name"]
    ordering = ["-created_on"]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} registered a new parent: {instance.full_name} (ID: {instance.id})"
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} updated parent: {instance.full_name} (ID: {instance.id})"
        )


@extend_schema(
    tags=["IfasheTugufashe - Work "],
)
class ParentWorkContractViewSet(viewsets.ModelViewSet):
    queryset = ParentWorkContract.objects.select_related("parent")
    serializer_class = ParentWorkContractSerializer
    permission_classes = [IsIfasheManager]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} created a work contract for parent {instance.parent} (ID: {instance.id})"
        )


@extend_schema(
    tags=["IfasheTugufashe - Work "],
)
class ParentAttendanceViewSet(viewsets.ModelViewSet):
    queryset = ParentAttendance.objects.select_related(
        "work_record", "work_record__parent"
    )
    serializer_class = ParentAttendanceSerializer
    permission_classes = [IsIfasheManager]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} recorded attendance ({instance.status}) for parent {instance.work_record.parent} on {instance.attendance_date}"
        )


@extend_schema(
    tags=["IfasheTugufashe - Work "],
)
class ParentPerformanceViewSet(viewsets.ModelViewSet):
    queryset = ParentPerformance.objects.select_related(
        "work_record", "work_record__parent", "evaluated_by"
    )
    serializer_class = ParentPerformanceSerializer
    permission_classes = [IsIfasheManager]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} submitted a performance evaluation (Rating: {instance.rating}) for parent {instance.work_record.parent}"
        )
