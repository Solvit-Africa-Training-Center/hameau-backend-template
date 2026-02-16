from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
)
import logging

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import Caretaker
from programs.serializers import (
    CaretakerReadSerializer,
    CaretakerWriteSerializer,
    CaretakerListSerializer,
)
from utils.paginators import StandardResultsSetPagination
from accounts.permissions import IsResidentialManager

logger = logging.getLogger(__name__)

@extend_schema_view(
    list=extend_schema(
        tags=["Residential Care Program - Caretakers"],
        summary="List caretakers",
        description=(
            "Retrieve a paginated list of caretakers. "
            "Supports search, ordering, and filtering."
        ),
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search by first name, last name, phone, email, or role",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="ordering",
                description="Order by first_name, last_name, hire_date, or created_on",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="active_only",
                description="Filter only active caretakers (`true`)",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="gender",
                description="Filter by gender",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="role",
                description="Filter by caretaker role (partial match)",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: CaretakerListSerializer(many=True),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    retrieve=extend_schema(
        tags=["Residential Care Program - Caretakers"],
        summary="Retrieve caretaker",
        description="Retrieve detailed information about a single caretaker.",
        responses={
            200: CaretakerReadSerializer,
            404: OpenApiResponse(description="Caretaker not found"),
        },
    ),
    create=extend_schema(
        tags=["Residential Care Program - Caretakers"],
        summary="Create caretaker",
        description="Create a new caretaker.",
        request=CaretakerWriteSerializer,
        responses={
            201: CaretakerReadSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    update=extend_schema(
        tags=["Residential Care Program - Caretakers"],
        summary="Update caretaker",
        description="Update an existing caretaker.",
        request=CaretakerWriteSerializer,
        responses={
            200: CaretakerReadSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    partial_update=extend_schema(
        tags=["Residential Care Program - Caretakers"],
        summary="Partially update caretaker",
        description="Partially update an existing caretaker.",
        request=CaretakerWriteSerializer,
        responses={
            200: CaretakerReadSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    destroy=extend_schema(
        tags=["Residential Care Program - Caretakers"],
        summary="Delete caretaker",
        description="Soft delete a caretaker.",
        responses={
            204: OpenApiResponse(description="Caretaker deleted successfully"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
)

class CaretakerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing caretakers.
    Provides CRUD operations, activation, deactivation, and statistics.
    """

    queryset = Caretaker.objects.filter(deleted_on__isnull=True)
    permission_classes = [IsAuthenticated, IsResidentialManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["first_name", "last_name", "phone", "email", "role"]
    ordering_fields = ["first_name", "last_name", "hire_date", "created_on"]
    ordering = ["-created_on"]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CaretakerWriteSerializer
        elif self.action == "list":
            return CaretakerListSerializer
        return CaretakerReadSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.request.query_params.get("active_only") == "true":
            queryset = queryset.filter(is_active=True)

        gender = self.request.query_params.get("gender")
        if gender:
            queryset = queryset.filter(gender=gender)

        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role__icontains=role)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {
                "success": True,
                "message": "Caretaker deleted successfully",
            },
            status=status.HTTP_204_NO_CONTENT,
        )

    @extend_schema(
        tags=["Residential Care Program - Caretakers"],
        summary="Activate caretaker",
        description="Activate a caretaker account.",
        responses={
            200: CaretakerReadSerializer,
            404: OpenApiResponse(description="Caretaker not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        caretaker = self.get_object()
        caretaker.is_active = True
        caretaker.save()

        serializer = self.get_serializer(caretaker)
        return Response(
            {
                "success": True,
                "message": "Caretaker activated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Residential Care Program - Caretakers"],
        summary="Deactivate caretaker",
        description="Deactivate a caretaker account.",
        responses={
            200: CaretakerReadSerializer,
            404: OpenApiResponse(description="Caretaker not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        caretaker = self.get_object()
        caretaker.is_active = False
        caretaker.save()

        serializer = self.get_serializer(caretaker)
        return Response(
            {
                "success": True,
                "message": "Caretaker deactivated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Residential Care Program - Caretakers"],
        summary="Caretaker statistics",
        description="Retrieve statistics about caretakers (total, active, inactive, gender breakdown).",
        responses={
            200: OpenApiResponse(description="Caretaker statistics"),
        },
    )
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        queryset = self.get_queryset()

        total_caretakers = queryset.count()
        active_caretakers = queryset.filter(is_active=True).count()
        inactive_caretakers = queryset.filter(is_active=False).count()

        male_count = queryset.filter(gender=Caretaker.MALE).count()
        female_count = queryset.filter(gender=Caretaker.FEMALE).count()

        return Response(
            {
                "success": True,
                "data": {
                    "total_caretakers": total_caretakers,
                    "active_caretakers": active_caretakers,
                    "inactive_caretakers": inactive_caretakers,
                    "gender_breakdown": {
                        "male": male_count,
                        "female": female_count,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )
