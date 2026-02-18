import logging
from rest_framework import viewsets, filters, serializers
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from utils.bulk_operations.mixins import BulkActionMixin
from utils.bulk_operations.tasks import generic_bulk_task

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
from drf_spectacular.utils import extend_schema, inline_serializer
from utils.bulk_operations.serializers import BulkActionSerializer


logger = logging.getLogger(__name__)


@extend_schema(
    tags=["IfasheTugufashe Program"],
)
class IfasheParentViewSet(BulkActionMixin, viewsets.ModelViewSet):
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
        description="Bulk delete supported parents. by providing a list of IDs.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkDeleteParentResponse",
                fields={
                    "message": serializers.CharField(),
                    "action": serializers.CharField(),
                    "count": serializers.IntegerField(),
                    "async": serializers.BooleanField(),
                },
            ),
            202: inline_serializer(
                name="BulkDeleteParentAsyncResponse",
                fields={
                    "message": serializers.CharField(),
                    "action": serializers.CharField(),
                    "count": serializers.IntegerField(),
                    "async": serializers.BooleanField(),
                },
            ),
        },
    )
    @action(detail=False, methods=["post"])
    def bulk_delete(self, request):
        return self.perform_bulk_action(
            request,
            action_type="delete",
            async_task=generic_bulk_task,
        )

    @extend_schema(
        description="Bulk update fields for a list of supported parents.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkUpdateParentResponse",
                fields={
                    "message": serializers.CharField(),
                    "action": serializers.CharField(),
                    "count": serializers.IntegerField(),
                    "updated_fields": serializers.ListField(
                        child=serializers.CharField()
                    ),
                    "async": serializers.BooleanField(),
                },
            ),
            400: inline_serializer(
                name="BulkUpdateParentError", fields={"detail": serializers.CharField()}
            ),
        },
    )
    @action(detail=False, methods=["post"])
    def bulk_update(self, request):
        return self.perform_bulk_action(
            request,
            action_type="update",
            async_task=generic_bulk_task,
        )


@extend_schema(
    tags=["IfasheTugufashe Program"],
)
class ParentWorkContractViewSet(BulkActionMixin, viewsets.ModelViewSet):
    queryset = ParentWorkContract.objects.select_related("parent")
    serializer_class = ParentWorkContractSerializer
    permission_classes = [IsIfasheManager]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} created a work contract for parent {instance.parent} (ID: {instance.id})"
        )


@extend_schema(
    tags=["IfasheTugufashe Program"],
)
class ParentAttendanceViewSet(BulkActionMixin, viewsets.ModelViewSet):
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
    tags=["IfasheTugufashe Program"],
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
