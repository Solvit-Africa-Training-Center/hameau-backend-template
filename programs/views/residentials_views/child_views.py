from rest_framework import viewsets, status, filters, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

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
    ChildProgressReportSerializer,
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
from utils.reports import generate_child_progress_pdf, PDFRenderer

from accounts.permissions import (
    IsResidentialManager,
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

    @action(detail=True, methods=["get"])
    def education(self, request, pk=None):
        child = self.get_object()
        education_records = child.education_records.all().order_by("-start_date")
        serializer = ChildEducationReadSerializer(education_records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], renderer_classes=[renderers.JSONRenderer, PDFRenderer])
    def download_progress_report(self, request, pk=None):
        child = self.get_object()
        
        # Get latest progress
        progress_queryset = child.child_progress.all() # Ordered by -created_on
        latest_progress = progress_queryset.first()
        
        if not latest_progress:
             return Response({"error": "No progress records found for this child"}, status=status.HTTP_404_NOT_FOUND)

        # Get previous progress (second latest)
        previous_progress = None
        if progress_queryset.count() > 1:
            previous_progress = progress_queryset[1]
            
        report_data = {
            'child': child,
            'latest_progress': latest_progress,
            'previous_progress': previous_progress
        }
        
        serializer = ChildProgressReportSerializer(report_data)
        return Response(serializer.data)


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
