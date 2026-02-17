import logging

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Sum, Avg, Max, Min
from decimal import Decimal
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from programs.models import HealthRecord, Child
from programs.serializers import (
    HealthRecordReadSerializer,
    HealthRecordWriteSerializer,
    HealthRecordListSerializer,
)
from utils.filters.health_records_filters import HealthRecordFilter
from utils.paginators import StandardResultsSetPagination
from utils.search import CustomSearchFilter
from accounts.permissions import IsResidentialManager

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(tags=["Residential Care Program"]),
    retrieve=extend_schema(tags=["Residential Care Program"]),
    create=extend_schema(tags=["Residential Care Program"]),
    update=extend_schema(tags=["Residential Care Program"]),
    partial_update=extend_schema(tags=["Residential Care Program"]),
    destroy=extend_schema(tags=["Residential Care Program"]),
)
class HealthRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthRecord.objects.select_related("child")
    permission_classes = [IsAuthenticated, IsResidentialManager]
    filter_backends = [
        DjangoFilterBackend,
        CustomSearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = HealthRecordFilter
    search_fields = [
        "diagnosis",
        "treatment",
        "hospital_name",
        "description",
        "child__first_name",
        "child__last_name",
    ]
    ordering_fields = [
        "visit_date",
        "created_on",
        "record_type",
        "hospital_name",
        "cost",
    ]
    ordering = ["-visit_date", "-created_on"]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return HealthRecordWriteSerializer
        elif self.action == "list":
            return HealthRecordListSerializer
        return HealthRecordReadSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        child_id = self.request.query_params.get("child_id")
        if child_id:
            queryset = queryset.filter(child_id=child_id)

        record_type = self.request.query_params.get("type")
        if record_type:
            queryset = queryset.filter(record_type=record_type)

        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if date_from:
            queryset = queryset.filter(visit_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(visit_date__lte=date_to)

        return queryset

    @extend_schema(tags=["Residential Care Program"])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        logger.info(
            f"Health record created: Child ID={serializer.instance.child_id}, "
            f"Type={serializer.instance.record_type}, Cost={serializer.instance.cost}, "
            f"by user {request.user.id}"
        )
        read_serializer = HealthRecordReadSerializer(serializer.instance)
        return Response(
            {
                "success": True,
                "message": "Health record created successfully",
                "data": read_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(tags=["Residential Care Program"])
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        read_serializer = HealthRecordReadSerializer(serializer.instance)
        return Response(
            {
                "success": True,
                "message": "Health record updated successfully",
                "data": read_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(tags=["Residential Care Program"])
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        logger.warning(
            f"Health record deleted: ID={instance.id}, Child ID={instance.child_id}, "
            f"by user {request.user.id}"
        )

        self.perform_destroy(instance)
        return Response(
            {"success": True, "message": "Health record deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @extend_schema(tags=["Residential Care Program"])
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        queryset = self.get_queryset()

        # Overall statistics
        total_records = queryset.count()

        # Cost statistics
        cost_stats = queryset.aggregate(
            total_cost=Sum("cost"),
            average_cost=Avg("cost"),
            max_cost=Max("cost"),
            min_cost=Min("cost"),
        )

        # Count by record type with cost breakdown
        records_by_type = (
            queryset.values("record_type")
            .annotate(
                count=Count("id"), total_cost=Sum("cost"), average_cost=Avg("cost")
            )
            .order_by("-total_cost")
        )

        # Recent records (last 30 days)
        from datetime import timedelta
        from django.utils import timezone

        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_records = queryset.filter(visit_date__gte=thirty_days_ago)
        recent_cost = recent_records.aggregate(total=Sum("cost"))["total"] or Decimal(
            "0.00"
        )

        children_with_records = queryset.values("child").distinct().count()

        return Response(
            {
                "success": True,
                "data": {
                    "total_records": total_records,
                    "recent_records_30_days": recent_records.count(),
                    "recent_cost_30_days": float(recent_cost),
                    "children_with_records": children_with_records,
                    "cost_statistics": {
                        "total_cost": float(cost_stats["total_cost"] or 0),
                        "average_cost": float(cost_stats["average_cost"] or 0),
                        "max_cost": float(cost_stats["max_cost"] or 0),
                        "min_cost": float(cost_stats["min_cost"] or 0),
                    },
                    "records_by_type": [
                        {
                            "record_type": item["record_type"],
                            "count": item["count"],
                            "total_cost": float(item["total_cost"] or 0),
                            "average_cost": float(item["average_cost"] or 0),
                        }
                        for item in records_by_type
                    ],
                },
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Residential Care Program"],
        parameters=[
            OpenApiParameter(
                name="child_id", description="ID of the child", required=True, type=int
            )
        ],
    )
    @action(detail=False, methods=["get"], url_path="child/(?P<child_id>[^/.]+)")
    def child_records(self, request, child_id=None):
        child = get_object_or_404(Child, pk=child_id)
        records = self.get_queryset().filter(child=child)

        total_cost = records.aggregate(total=Sum("cost"))["total"] or Decimal("0.00")
        average_cost = records.aggregate(avg=Avg("cost"))["avg"] or Decimal("0.00")

        page = self.paginate_queryset(records)
        if page is not None:
            serializer = HealthRecordReadSerializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data["child_name"] = f"{child.first_name} {child.last_name}"
            response_data["cost_summary"] = {
                "total_cost": float(total_cost),
                "average_cost": float(average_cost),
                "record_count": records.count(),
            }
            return Response(response_data)

        serializer = HealthRecordReadSerializer(records, many=True)
        return Response(
            {
                "success": True,
                "child_name": f"{child.first_name} {child.last_name}",
                "count": records.count(),
                "cost_summary": {
                    "total_cost": float(total_cost),
                    "average_cost": float(average_cost),
                },
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Residential Care Program"],
        parameters=[
            OpenApiParameter(
                name="condition",
                description="Condition to filter by (diagnosis, treatment, or description)",
                required=True,
                type=str,
            )
        ],
    )
    @action(detail=False, methods=["get"])
    def by_condition(self, request):
        condition = request.query_params.get("condition")

        if not condition:
            return Response(
                {"success": False, "message": "Condition parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        records = self.get_queryset().filter(
            Q(diagnosis__icontains=condition)
            | Q(treatment__icontains=condition)
            | Q(description__icontains=condition)
        )

        total_cost = records.aggregate(total=Sum("cost"))["total"] or Decimal("0.00")

        page = self.paginate_queryset(records)
        if page is not None:
            serializer = HealthRecordListSerializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data["condition"] = condition
            response_data["total_cost"] = float(total_cost)
            return Response(response_data)

        serializer = HealthRecordListSerializer(records, many=True)
        return Response(
            {
                "success": True,
                "condition": condition,
                "count": records.count(),
                "total_cost": float(total_cost),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
