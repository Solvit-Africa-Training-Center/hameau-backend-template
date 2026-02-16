from rest_framework import viewsets, filters, serializers
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer

from programs.models import SponsoredChild, DressingDistribution
from programs.serializers.ifashe_serializers import (
    IfasheChildSerializer,
    DressingDistributionSerializer,
)
from accounts.permissions import IsIfasheManager

from utils.bulk_operations.mixins import BulkActionMixin
from utils.bulk_operations.tasks import generic_bulk_task
from utils.bulk_operations.serializers import BulkActionSerializer


@extend_schema(tags=["IfasheTugufashe Program"])
class IfasheChildViewSet(BulkActionMixin, viewsets.ModelViewSet):
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

    bulk_max_size = 200
    bulk_async_threshold = 30

    @extend_schema(
        description="Bulk delete supported children. by providing a list of IDs.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkDeleteIChildResponse",
                fields={
                    "message": serializers.CharField(),
                    "action": serializers.CharField(),
                    "count": serializers.IntegerField(),
                    "async": serializers.BooleanField(),
                },
            ),
            202: inline_serializer(
                name="BulkDeleteIChildAsyncResponse",
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
        description="Bulk update fields for a list of supported children.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkUpdateIChildResponse",
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
                name="BulkUpdateIChildError", fields={"detail": serializers.CharField()}
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
        description="Bulk update status of children as exited the program.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkUpdateChildExitResponse",
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
                name="BulkUpdateChildExitError",
                fields={"detail": serializers.CharField()},
            ),
        },
    )
    @action(detail=False, methods=["post"])
    def bulk_exit_program(self, request):

        def exit_program(queryset, payload):
            count = queryset.update(support_status=SponsoredChild.EXITED)
            return {
                "message": "Children marked as exited the program.",
                "count": count,
            }

        return self.perform_bulk_action(
            request,
            action_type="custom",
            custom_handler=exit_program,
        )


@extend_schema(tags=["IfasheTugufashe Program"])
class DressingDistributionViewSet(BulkActionMixin, viewsets.ModelViewSet):
    queryset = DressingDistribution.objects.select_related("child")
    serializer_class = DressingDistributionSerializer
    permission_classes = [IsIfasheManager]

    bulk_async_threshold = 50

    @extend_schema(
        description="Bulk delete internship applications by providing a list of IDs.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkDeleteDressingResponse",
                fields={
                    "message": serializers.CharField(),
                    "action": serializers.CharField(),
                    "count": serializers.IntegerField(),
                    "async": serializers.BooleanField(),
                },
            ),
            202: inline_serializer(
                name="BulkDeleteDressingAsyncResponse",
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
                name="BulkUpdateDressingResponse",
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
                name="BulkUpdateDressingError",
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
