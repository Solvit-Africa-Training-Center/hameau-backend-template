import logging

from django.http import FileResponse
from rest_framework import viewsets, status, filters, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    extend_schema_view,
    OpenApiParameter,
)


from programs.models import (
    Child,
    ChildProgress,
    ProgressMedia,
    ChildEducation,
    EducationInstitution,
    EducationProgram,
)
from programs.serializers import (
    ChildReadSerializer,
    ChildWriteSerializer,
    ChildProgressReadSerializer,
    ChildProgressWriteSerializer,
    ChildEducationReadSerializer,
    ChildEducationWriteSerializer,
    EducationInstitutionSerializer,
    EducationProgramReadSerializer,
    EducationProgramWriteSerializer,
)
from utils.filters.child_filters import (
    ChildFilter,
    ChildProgressFilter,
    ChildEducationFilter,
    EducationProgramFilter,
)
from utils.paginators import (
    StandardResultsSetPagination,
    ProgressCursorPagination,
    SmallResultsSetPagination,
)
from utils.reports.general_reports import generate_child_progress_pdf
from utils.reports.ifashe.helpers import safe_filename

from accounts.models import User
from utils.activity_log import record_activity
from accounts.permissions import (
    IsResidentialManager,
)

logger = logging.getLogger(__name__)

@extend_schema_view(
    list=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="List children",
        description="Retrieve a paginated list of children with filtering, search, and ordering.",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search by first name, last name, or story",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="ordering",
                description="Order by first_name, last_name, date_of_birth, start_date, or created_on",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="active_only",
                description="Return only active children (`true`)",
                required=False,
                type=bool,
            ),
        ],
        responses={
            200: ChildReadSerializer(many=True),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    retrieve=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Retrieve child",
        description="Retrieve detailed information about a specific child.",
        responses={
            200: ChildReadSerializer,
            404: OpenApiResponse(description="Child not found"),
        },
    ),
    create=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Create child",
        description="Create a new child record.",
        request=ChildWriteSerializer,
        responses={
            201: ChildReadSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    ),
    update=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Update child",
        description="Update an existing child record.",
        request=ChildWriteSerializer,
        responses={
            200: ChildReadSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    ),
    partial_update=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Partially update child",
        description="Partially update an existing child record.",
        request=ChildWriteSerializer,
        responses={
            200: ChildReadSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    ),
    destroy=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Delete child",
        description="Delete a child record.",
        responses={
            204: OpenApiResponse(description="Child deleted successfully"),
        },
    ),
)
class ChildViewSet(viewsets.ModelViewSet):
    queryset = (
        Child.objects.all()
        .select_related()
        .prefetch_related("child_progress", "education_records")
    )
    permission_classes = [IsAuthenticated, IsResidentialManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ChildFilter
    search_fields = ["first_name", "last_name", "story"]
    ordering_fields = [
        "first_name",
        "last_name",
        "date_of_birth",
        "start_date",
        "created_on",
    ]
    ordering = ["-created_on"]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ChildWriteSerializer
        return ChildReadSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get("active_only") == "true":
            queryset = queryset.filter(status="active")

        return queryset
    
        
    def perform_create(self, serializer):
        child = serializer.save()
        logger.info(
            f"New child created: ID={child.id}, Name={child.first_name} {child.last_name}, "
            f"by user {self.request.user.id}"
        )
        record_activity(
            self.request,
            action="CREATE",
            resource="Child",
            resource_id=str(child.id),
            details={"name": f"{child.first_name} {child.last_name}"}
        )

    def perform_update(self, serializer):
        child = serializer.save()
        logger.info(
            f"Child updated: ID={child.id}, by user {self.request.user.id}"
        )
        record_activity(
            self.request,
            action="UPDATE",
            resource="Child",
            resource_id=str(child.id),
            details={"name": f"{child.first_name} {child.last_name}"}
        )

    def perform_destroy(self, instance):
        logger.warning(
            f"Child deleted: ID={instance.id}, Name={instance.first_name} {instance.last_name}, "
            f"by user {self.request.user.id}"
        )
        record_activity(
            self.request,
            action="DELETE",
            resource="Child",
            resource_id=str(instance.id),
            details={"name": f"{instance.first_name} {instance.last_name}"}
        )
        instance.delete()

    @extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Child progress list",
        description="Retrieve progress history for a specific child.",
        responses={200: ChildProgressReadSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        child = self.get_object()
        progress_entries = child.child_progress.all().order_by("-created_on")

        page = self.paginate_queryset(progress_entries)
        if page is not None:
            serializer = ChildProgressReadSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ChildProgressReadSerializer(progress_entries, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Add child progress",
        description="Add a new progress entry for a specific child.",
        request=ChildProgressWriteSerializer,
        responses={
            201: ChildProgressReadSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    @action(detail=True, methods=["post"])
    def add_progress(self, request, pk=None):
        child = self.get_object()

        serializer = ChildProgressWriteSerializer(
            data=request.data, context={"child": child, "request": request}
        )

        if serializer.is_valid():
            progress = serializer.save()
            read_serializer = ChildProgressReadSerializer(progress)
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Child education records",
        description="Retrieve education records for a specific child.",
        responses={200: ChildEducationReadSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def education(self, request, pk=None):
        child = self.get_object()
        education_records = child.education_records.all().order_by("-start_date")
        serializer = ChildEducationReadSerializer(education_records, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Download child progress report",
        description="Generate and download the latest child progress report",
        responses={
            200: OpenApiResponse(description="PDF file response"),
            404: OpenApiResponse(description="No progress records found"),
        },
    )
    @action(
        detail=True,
        methods=["get"],
    )
    def download_progress_report(self, request, pk=None):
        child = self.get_object()

        progress_queryset = child.child_progress.all()
        latest_progress = progress_queryset.first()

        if not latest_progress:
            return Response(
                {"error": "No progress records found for this child"},
                status=status.HTTP_404_NOT_FOUND,
            )

        previous_progress = None
        if progress_queryset.count() > 1:
            previous_progress = progress_queryset[1]

        filename = safe_filename(f"child_progress_report_{child.id}", "pdf")
        path = f"/tmp/{filename}"

        buffer = generate_child_progress_pdf(child, latest_progress, previous_progress)

        with open(path, "wb") as f:
            f.write(buffer.getvalue())

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )


@extend_schema_view(
    list=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="List child progress",
        description="Retrieve a paginated list of child progress entries.",
        responses={200: ChildProgressReadSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Retrieve child progress",
        responses={200: ChildProgressReadSerializer},
    ),
    create=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Create child progress",
        description="Create a child progress entry (child_id required).",
        request=ChildProgressWriteSerializer,
        responses={201: ChildProgressReadSerializer},
    ),
    update=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Update child progress",
        request=ChildProgressWriteSerializer,
        responses={200: ChildProgressReadSerializer},
    ),
    partial_update=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Partially update child progress",
        request=ChildProgressWriteSerializer,
        responses={200: ChildProgressReadSerializer},
    ),
    destroy=extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Delete child progress",
        responses={204: OpenApiResponse(description="Deleted successfully")},
    ),
)
class ChildProgressViewSet(viewsets.ModelViewSet):
    """
    Manage child progress CRUD
    """

    queryset = ChildProgress.objects.select_related("child").prefetch_related(
        "progress_media",
        "child__education_records",
    )
    permission_classes = [IsAuthenticated, IsResidentialManager]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ChildProgressFilter
    ordering_fields = ["created_on"]
    ordering = ["-created_on"]
    pagination_class = ProgressCursorPagination

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ChildProgressWriteSerializer
        return ChildProgressReadSerializer

    def perform_create(self, serializer):
        child_id = self.request.data.get("child_id")
        if not child_id:
            return Response(
                {"error": "child_id required"}, status=status.HTTP_400_BAD_REQUEST
            )

        child = get_object_or_404(Child, pk=child_id)
        serializer.save(context={"child": child})

    @extend_schema(
        tags=["Residential Care Program - Children"],
        summary="Add child progress media",
        description="Upload image and/or video media for a progress entry.",
        responses={
            201: ChildProgressReadSerializer,
            400: OpenApiResponse(description="No media found"),
        },
    )
    @action(detail=True, methods=["post"])
    def add_media(self, request, pk=None):
        progress = self.get_object()
        media_items = []
        errors = []

        if "progress_image" in request.FILES:
            media = ProgressMedia.objects.create(
                progress=progress, progress_image=request.FILES["progress_image"]
            )
            media_items.append(media)

        if "progress_video" in request.FILES:
            media = ProgressMedia.objects.create(
                progress=progress, progress_video=request.FILES["progress_video"]
            )
            media_items.append(media)

        if not media_items:
            return Response(
                {"error": "No media found"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ChildProgressReadSerializer(progress)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    create=(
        extend_schema(
            tags=["Residential Care Program - Education Institutions"],
            summary="Create education institution",
            request=EducationInstitutionSerializer,
            responses={201: EducationInstitutionSerializer},
        ),
    ),
    update=(
        extend_schema(
            tags=["Residential Care Program - Education Institutions"],
            summary="Update education institution",
            request=EducationInstitutionSerializer,
            responses={200: EducationInstitutionSerializer},
        ),
    ),
    partial_update=(
        extend_schema(
            tags=["Residential Care Program - Education Institutions"],
            summary="Partially update education institution",
            request=EducationInstitutionSerializer,
            responses={200: EducationInstitutionSerializer},
        ),
    ),
    destroy=(
        extend_schema(
            tags=["Residential Care Program - Education Institutions"],
            summary="Delete education institution",
            responses={204: OpenApiResponse(description="Deleted successfully")},
        ),
    ),
)
@extend_schema_view(
    list=extend_schema(tags=["Residential Care Program - Education Institutions"]),
    retrieve=extend_schema(tags=["Residential Care Program - Education Institutions"]),
    create=extend_schema(tags=["Residential Care Program - Education Institutions"]),
    update=extend_schema(tags=["Residential Care Program - Education Institutions"]),
    partial_update=extend_schema(
        tags=["Residential Care Program - Education Institutions"]
    ),
    destroy=extend_schema(tags=["Residential Care Program - Education Institutions"]),
    programs=extend_schema(
        tags=["Residential Care Program - Education Institutions"],
        responses={
            200: EducationProgramReadSerializer(many=True)
        },  
    ),
)
class EducationInstitutionViewSet(viewsets.ModelViewSet):
    queryset = EducationInstitution.objects.all().prefetch_related("programs")
    serializer_class = EducationInstitutionSerializer
    permission_classes = [IsAuthenticated, IsResidentialManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["name", "created_on"]
    ordering = ["name"]
    pagination_class = SmallResultsSetPagination

    @action(detail=True, methods=["get"])
    def programs(self, request, pk=None):
        institution = self.get_object()
        programs = institution.programs.all()

        serializer = EducationProgramReadSerializer(programs, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=["Residential Care Program - Education "],
)
class EducationProgramViewSet(viewsets.ModelViewSet):
    queryset = EducationProgram.objects.all().select_related("institution")
    permission_classes = [IsAuthenticated, IsResidentialManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = EducationProgramFilter
    search_fields = ["program_name", "program_level"]
    ordering_fields = ["program_name", "cost", "created_on"]
    ordering = ["program_name"]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return EducationProgramWriteSerializer
        return EducationProgramReadSerializer

    @action(detail=True, methods=["get"])
    def program_enrollments(self, request, pk=None):
        program = self.get_object()
        enrollments = ChildEducation.objects.filter(program=program).select_related(
            "child"
        )

        serializer = ChildEducationReadSerializer(enrollments, many=True)
        return Response(serializer.data)


@extend_schema(
    tags=["Residential Care Program - Education "],
)
class ChildEducationViewSet(viewsets.ModelViewSet):
    queryset = ChildEducation.objects.all().select_related(
        "child", "program", "program__institution"
    )
    permission_classes = [IsAuthenticated, IsResidentialManager]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ChildEducationFilter
    ordering_fields = ["start_date", "end_date", "cost", "created_on"]
    ordering = ["-start_date"]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ChildEducationWriteSerializer
        return ChildEducationReadSerializer
