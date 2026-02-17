from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer

from accounts.permissions import IsInternshipManager
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from ...models.internships_models import InternshipApplication
from ...serializers.internships_serializers import InternshipApplicationSerializer
from utils.paginators import StandardResultsSetPagination

from utils.bulk_operations.mixins import BulkActionMixin
from utils.bulk_operations.tasks import generic_bulk_task
from utils.bulk_operations.serializers import BulkActionSerializer


@extend_schema(
    tags=["Internship - Applications"],
)
class InternshipApplicationViewSet(BulkActionMixin, viewsets.ModelViewSet):
    queryset = InternshipApplication.objects.all().order_by("-applied_on")
    serializer_class = InternshipApplicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["country", "education_level", "status"]
    search_fields = ["first_name", "last_name", "email", "phone", "school_university"]
    ordering_fields = ["applied_on", "status"]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated(), IsInternshipManager()]

    @extend_schema(
        description="Bulk delete internship applications by providing a list of IDs.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkDeleteApplicationResponse",
                fields={
                    "message": serializers.CharField(),
                    "action": serializers.CharField(),
                    "count": serializers.IntegerField(),
                    "async": serializers.BooleanField(),
                },
            ),
            202: inline_serializer(
                name="BulkDeleteApplicationAsyncResponse",
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
        description="Bulk update fields for a list of internship applications.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkUpdateApplicationResponse",
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
                name="BulkUpdateApplicationError",
                fields={"detail": serializers.CharField()},
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
