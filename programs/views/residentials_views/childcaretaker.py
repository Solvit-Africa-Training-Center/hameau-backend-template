from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from programs.models import ChildCaretakerAssignment, House
from programs.serializers import (
    ChildCaretakerAssignmentReadSerializer,
    ChildCaretakerAssignmentWriteSerializer,
)
from django.db import transaction
from accounts.permissions import IsResidentialManager
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
    inline_serializer,
)


@extend_schema_view(
    list=extend_schema(
        tags=["Residential Care Program"],
        summary="List child-caretaker assignments",
        responses={200: ChildCaretakerAssignmentReadSerializer(many=True)},
    ),
    create=extend_schema(
        tags=["Residential Care Program"],
        summary="Assign child to caretaker",
        request=ChildCaretakerAssignmentWriteSerializer,
        responses={201: ChildCaretakerAssignmentReadSerializer},
    ),
)
class ChildCaretakerAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ChildCaretakerAssignment.objects.select_related(
        "child", "house__caretaker"
    ).all()

    permission_classes = [IsAuthenticated, IsResidentialManager]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update", "bulk_assign"]:
            return ChildCaretakerAssignmentWriteSerializer
        return ChildCaretakerAssignmentReadSerializer

    @extend_schema(
        tags=["Residential Care Program"],
        summary="Assign a child to a catetaker",
        description="""
                    Assign a child to a specific caretaker.

                    Business rules:
                    - A child cannot have multiple active assignments for the same caretaker.
                    - `assigned_date` is automatically set to today's date.
                    """,
        request=ChildCaretakerAssignmentWriteSerializer,
        responses={
            201: ChildCaretakerAssignmentReadSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["Residential Care Program"],
        summary="Bulk assign children to a caretaker",
        description="""
Assign multiple children to a specific caretaker.

Rules:
- caretaker_id is required.
- children_ids must be a list of child UUIDs.
- Duplicate active assignments are ignored.
""",
        request=inline_serializer(
            name="BulkAssignChildrenRequest",
            fields={
                "caretaker_id": serializers.UUIDField(),
                "children_ids": serializers.ListField(child=serializers.UUIDField()),
            },
        ),
        responses={
            201: ChildCaretakerAssignmentReadSerializer(many=True),
            400: OpenApiResponse(description="Validation error"),
        },
    )
    @action(detail=False, methods=["post"])
    def bulk_assign(self, request):

        caretaker_id = request.data.get("caretaker_id")
        children_ids = request.data.get("children_ids", [])        

        results = []

        with transaction.atomic():
            for child_id in children_ids:
                try:
                    house = (
                        House.objects
                        .select_related("caretaker")
                        .get(caretaker_id=caretaker_id)
                    )
                except House.DoesNotExist:
                    raise serializers.ValidationError(
                        {"caretaker_id": "No house found for this caretaker."}
                    )
                assignment, created = ChildCaretakerAssignment.objects.get_or_create(
                    child_id=child_id,
                    house=house,
                    is_active=True,
                    defaults={"assigned_date": timezone.now().date()},
                )
                results.append(assignment)

        serializer = ChildCaretakerAssignmentReadSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["Residential Care Program"],
        summary="Remove a child-caretaker assignment",
        description="""
Delete a specific assignment by ID.

This permanently removes the assignment record.
""",
        responses={
            204: OpenApiResponse(description="Assignment deleted successfully"),
            404: OpenApiResponse(description="Assignment not found"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
    tags=["Residential Care Program"],
    summary="Bulk remove child-catetaker assignments",
    description="""
Delete multiple assignments by providing a list of assignment IDs.
""",
    request=inline_serializer(
        name="BulkRemoveAssignmentsRequest",
        fields={
            "caretaker_id": serializers.UUIDField(),
            "assignment_ids": serializers.ListField(
                child=serializers.UUIDField()
            )
        },
    ),
    responses={
        200: inline_serializer(
            name="BulkRemoveAssignmentsResponse",
            fields={
                "deleted": serializers.IntegerField(),
            },
        ),
        400: OpenApiResponse(description="Validation error"),
    },
)
    @action(detail=False, methods=["post"])
    def bulk_remove(self, request):

        assignment_ids = request.data.get("assignment_ids", [])

        deleted_count, _ = ChildCaretakerAssignment.objects.filter(
            id__in=assignment_ids
        ).delete()

        return Response(
            {"deleted": deleted_count},
            status=status.HTTP_200_OK,
        )
