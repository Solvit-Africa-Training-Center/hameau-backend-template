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


@extend_schema(
    tags=["IfasheTugufashe - Work "],
)
class ParentWorkContractViewSet(viewsets.ModelViewSet):
    queryset = ParentWorkContract.objects.select_related("parent")
    serializer_class = ParentWorkContractSerializer
    permission_classes = [IsIfasheManager]


@extend_schema(
    tags=["IfasheTugufashe - Work "],
)
class ParentAttendanceViewSet(viewsets.ModelViewSet):
    queryset = ParentAttendance.objects.select_related(
        "work_record", "work_record__parent"
    )
    serializer_class = ParentAttendanceSerializer
    permission_classes = [IsIfasheManager]


@extend_schema(
    tags=["IfasheTugufashe - Work "],
)
class ParentPerformanceViewSet(viewsets.ModelViewSet):
    queryset = ParentPerformance.objects.select_related(
        "work_record", "work_record__parent", "evaluated_by"
    )
    serializer_class = ParentPerformanceSerializer
    permission_classes = [IsIfasheManager]
