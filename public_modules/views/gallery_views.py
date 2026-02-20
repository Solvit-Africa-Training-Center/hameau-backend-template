from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes

from public_modules.models.gallery_models import GalleryCategory, GalleryMedia
from ..serializers.gallery_serializers import (
    GalleryCategorySerializer,
    GalleryCategoryDetailSerializer,
    GalleryMediaSerializer,
    GalleryMediaListSerializer,
    BulkGalleryMediaUploadSerializer,
    BulkUploadResponseSerializer,
    CategoryStatsResponseSerializer,
)
from ..pagination import PublicModulePagination


@extend_schema_view(
    list=extend_schema(
        summary="List all gallery categories",
        description="Get a list of all gallery categories with media count",
        tags=["Public Modules"],
        responses={200: GalleryCategorySerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Get category details",
        description="Retrieve a specific category with all its media items",
        tags=["Public Modules"],
        responses={200: GalleryCategoryDetailSerializer},
    ),
    create=extend_schema(
        summary="Create new category",
        description="Create a new gallery category (Authentication required)",
        tags=["Public Modules"],
        request=GalleryCategorySerializer,
        responses={
            201: GalleryCategorySerializer,
            401: OpenApiResponse(description="Authentication required"),
        },
        examples=[
            OpenApiExample(
                "Create Events Category",
                value={
                    "name": "Events",
                    "description": "Photos and videos from various events",
                },
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        summary="Update category (full)",
        description="Update all fields of a category (Authentication required)",
        tags=["Public Modules"],
        request=GalleryCategorySerializer,
        responses={200: GalleryCategorySerializer},
    ),
    partial_update=extend_schema(
        summary="Update category (partial)",
        description="Update specific fields of a category (Authentication required)",
        tags=["Public Modules"],
        request=GalleryCategorySerializer,
        responses={200: GalleryCategorySerializer},
        examples=[
            OpenApiExample(
                "Update Description",
                value={"description": "Updated description"},
                request_only=True,
            ),
        ],
    ),
    destroy=extend_schema(
        summary="Delete category",
        description="Delete a category and all its media items (Authentication required)",
        tags=["Public Modules"],
        responses={
            204: OpenApiResponse(description="Category deleted successfully"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
)
class GalleryCategoryViewSet(viewsets.ModelViewSet):
    queryset = GalleryCategory.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_on", "updated_on"]
    ordering = ["name"]
    pagination_class = PublicModulePagination

    def get_serializer_class(self):
        """Use detailed serializer for retrieve action"""
        if self.action == "retrieve":
            return GalleryCategoryDetailSerializer
        return GalleryCategorySerializer

    @extend_schema(
        summary="Get category media",
        description="Get all media items for a specific category",
        tags=["Public Modules"],
        parameters=[
            OpenApiParameter(
                name="is_public",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by public/private status",
                required=False,
            ),
        ],
        responses={200: GalleryMediaListSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def media(self, request, pk=None):
        """Get all media items for a specific category"""
        category = self.get_object()
        media_items = category.media_items.all()

        # Apply filters
        is_public = request.query_params.get("is_public")
        if is_public is not None:
            is_public_bool = is_public.lower() in ("true", "1", "yes")
            media_items = media_items.filter(is_public=is_public_bool)

        serializer = GalleryMediaListSerializer(media_items, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get category statistics",
        description="Get statistics about all gallery categories including media counts",
        tags=["Public Modules"],
        responses={200: CategoryStatsResponseSerializer},
        examples=[
            OpenApiExample(
                "Category Stats Response",
                value={
                    "total_categories": 3,
                    "categories": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Events",
                            "media_count": 25,
                            "public_media_count": 20,
                        }
                    ],
                },
                response_only=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get statistics about gallery categories"""
        categories = self.get_queryset()
        stats = {"total_categories": categories.count(), "categories": []}

        for category in categories:
            stats["categories"].append(
                {
                    "id": str(category.id),
                    "name": category.name,
                    "media_count": category.media_items.count(),
                    "public_media_count": category.media_items.filter(
                        is_public=True
                    ).count(),
                }
            )

        return Response(stats)


@extend_schema_view(
    list=extend_schema(
        summary="List all media items",
        description="Get a paginated list of all media items with filtering and search",
        tags=["Public Modules"],
        parameters=[
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description="Filter by category UUID",
            ),
            OpenApiParameter(
                name="is_public",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by public/private status",
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search in title and description",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Order by field (e.g., -created_on, title)",
            ),
        ],
        responses={200: GalleryMediaListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Get media details",
        description="Retrieve detailed information about a specific media item",
        tags=["Public Modules"],
        responses={200: GalleryMediaSerializer},
    ),
    create=extend_schema(
        summary="Upload single image",
        description="Upload a single image to a category (Authentication required)",
        tags=["Public Modules"],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "format": "uuid"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "media_url": {"type": "string", "format": "binary"},
                    "is_public": {"type": "boolean"},
                },
            }
        },
        responses={
            201: GalleryMediaSerializer,
            401: OpenApiResponse(description="Authentication required"),
        },
    ),
    update=extend_schema(
        summary="Update media (full)",
        description="Update all fields of a media item (Authentication required)",
        tags=["Public Modules"],
        responses={200: GalleryMediaSerializer},
    ),
    partial_update=extend_schema(
        summary="Update media (partial)",
        description="Update specific fields of a media item (Authentication required)",
        tags=["Public Modules"],
        responses={200: GalleryMediaSerializer},
    ),
    destroy=extend_schema(
        summary="Delete media",
        description="Delete a media item (Only owner or staff)",
        tags=["Public Modules"],
        responses={
            204: OpenApiResponse(description="Media deleted successfully"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
)
class GalleryMediaViewSet(viewsets.ModelViewSet):
    queryset = GalleryMedia.objects.select_related("category", "uploaded_by").all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "is_public", "uploaded_by"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "created_on", "updated_on"]
    ordering = ["-created_on"]
    pagination_class = PublicModulePagination

    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action == "list":
            return GalleryMediaListSerializer
        elif self.action == "bulk_upload":
            return BulkGalleryMediaUploadSerializer
        return GalleryMediaSerializer

    def get_queryset(self):
        """Filter queryset based on permissions"""
        queryset = super().get_queryset()

        # Non-authenticated users only see public media
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)

        return queryset

    @extend_schema(
        summary="Bulk upload images",
        description="Upload multiple images (up to 50) to a category at once",
        tags=["Public Modules"],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "format": "uuid",
                        "description": "Category UUID",
                    },
                    "images": {
                        "type": "array",
                        "items": {"type": "string", "format": "binary"},
                        "description": "Array of image files (max 50)",
                    },
                    "title_prefix": {
                        "type": "string",
                        "description": "Optional prefix for auto-generated titles",
                    },
                    "description": {
                        "type": "string",
                        "description": "Common description for all images",
                    },
                    "is_public": {
                        "type": "boolean",
                        "default": True,
                        "description": "Make all images public",
                    },
                },
                "required": ["category", "images"],
            }
        },
        responses={
            201: BulkUploadResponseSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication required"),
        },
        examples=[
            OpenApiExample(
                "Successful Upload",
                value={
                    "message": "Successfully uploaded 5 images",
                    "count": 5,
                    "media_items": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "category": "123e4567-e89b-12d3-a456-426614174001",
                            "category_name": "Events",
                            "title": "Event 2024 1",
                            "media_url": "/media/media_gallery/image1.jpg",
                            "is_public": True,
                            "created_on": "2024-01-15T10:30:00Z",
                        }
                    ],
                },
                response_only=True,
            ),
        ],
    )
    @action(
        detail=False, methods=["post"], parser_classes=[MultiPartParser, FormParser]
    )
    def bulk_upload(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create media items
        created_media = serializer.save()

        # Return created media items
        response_serializer = GalleryMediaListSerializer(created_media, many=True)

        return Response(
            {
                "message": f"Successfully uploaded {len(created_media)} images",
                "count": len(created_media),
                "media_items": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Get my uploads",
        description="Get all media items uploaded by the current user",
        tags=["Public Modules"],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "count": {"type": "integer"},
                    "results": {"type": "array", "items": {}},
                },
            },
            401: OpenApiResponse(description="Authentication required"),
        },
    )
    @action(detail=False, methods=["get"])
    def my_uploads(self, request):

        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        media_items = self.get_queryset().filter(uploaded_by=request.user)
        serializer = GalleryMediaListSerializer(media_items, many=True)

        return Response({"count": media_items.count(), "results": serializer.data})

    @extend_schema(
        summary="Get public media",
        description="Get all public media items",
        tags=["Public Modules"],
        responses={200: GalleryMediaListSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def public(self, request):

        media_items = self.get_queryset().filter(is_public=True)
        serializer = GalleryMediaListSerializer(media_items, many=True)

        return Response({"count": media_items.count(), "results": serializer.data})

    @extend_schema(
        summary="Toggle media visibility",
        description="Toggle the public/private status of a media item",
        tags=["Public Modules"],
        request=None,
        responses={
            200: GalleryMediaSerializer,
            403: OpenApiResponse(description="Permission denied"),
        },
        examples=[
            OpenApiExample(
                "Visibility Toggled",
                value={
                    "message": "Media is now private",
                    "media": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "is_public": False,
                    },
                },
                response_only=True,
            ),
        ],
    )
    @action(detail=True, methods=["post"])
    def toggle_visibility(self, request, pk=None):

        media = self.get_object()

        # Check if user has permission to modify
        if media.uploaded_by != request.user and not request.user.is_staff:
            return Response(
                {"error": "You do not have permission to modify this media"},
                status=status.HTTP_403_FORBIDDEN,
            )

        media.is_public = not media.is_public
        media.save()

        serializer = self.get_serializer(media)
        return Response(
            {
                "message": f"Media is now {'public' if media.is_public else 'private'}",
                "media": serializer.data,
            }
        )

    def destroy(self, request, *args, **kwargs):

        media = self.get_object()

        # Only the uploader or staff can delete
        if media.uploaded_by != request.user and not request.user.is_staff:
            return Response(
                {"error": "You do not have permission to delete this media"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)
