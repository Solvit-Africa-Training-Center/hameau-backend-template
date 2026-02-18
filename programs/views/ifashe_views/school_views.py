from rest_framework import viewsets, filters, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from drf_spectacular.utils import extend_schema, inline_serializer

from programs.models.ifashe_models import SchoolSupport
from programs.serializers.ifashe_serializers import (
    SchoolSupportSerializer,
    SchoolPaymentSerializer,
)
from accounts.permissions import IsIfasheManager

from utils.bulk_operations.mixins import BulkActionMixin
from utils.bulk_operations.tasks import generic_bulk_task
from utils.bulk_operations.serializers import BulkActionSerializer


@extend_schema(tags=["IfasheTugufashe Program"])
class SchoolSupportViewSet(BulkActionMixin, viewsets.ModelViewSet):
    queryset = SchoolSupport.objects.all().prefetch_related("payments")
    serializer_class = SchoolSupportSerializer
    permission_classes = [IsIfasheManager]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["payment_status", "academic_year", "school"]
    search_fields = ["child__first_name", "child__last_name", "school__name"]
    ordering_fields = ["created_on", "academic_year"]

    bulk_max_size = 200
    bulk_async_threshold = 30

    @action(detail=True, methods=["post"])
    def add_payment(self, request, pk=None):
        school_support = self.get_object()
        serializer = SchoolPaymentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(school_support=school_support)

            total_paid = (
                school_support.payments.aggregate(total=models.Sum("amount"))["total"]
                or 0
            )

            if school_support.total_cost - total_paid <= 0:
                school_support.payment_status = SchoolSupport.PAID
                school_support.save(update_fields=["payment_status"])

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Bulk delete supports. by providing a list of IDs.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkDeleteSupportResponse",
                fields={
                    "message": serializers.CharField(),
                    "action": serializers.CharField(),
                    "count": serializers.IntegerField(),
                    "async": serializers.BooleanField(),
                },
            ),
            202: inline_serializer(
                name="BulkDeleteSupportAsyncResponse",
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
        description="Bulk update fields for a list of supports school.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkUpdateSupportResponse",
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
                name="BulkUpdateSupportError",
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

    @extend_schema(
        description="Bulk mark selected supports as paid.",
        request=BulkActionSerializer,
        responses={
            200: inline_serializer(
                name="BulkUpdateSupportPaidResponse",
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
                name="BulkUpdateSupportPaidError",
                fields={"detail": serializers.CharField()},
            ),
        },
    )
    @action(detail=False, methods=["post"])
    def bulk_mark_paid(self, request):

        def mark_paid(queryset, payload):
            count = queryset.update(payment_status=SchoolSupport.PAID)
            return {
                "message": "Selected supports marked as PAID.",
                "count": count,
            }

        return self.perform_bulk_action(
            request,
            action_type="custom",
            custom_handler=mark_paid,
        )
