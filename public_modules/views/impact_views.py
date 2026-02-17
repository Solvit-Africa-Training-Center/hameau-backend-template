from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view

from ..models.impact_models import ContactMessage, ImpactStatistic, ContactInfo
from ..serializers.impact_serializers import (
    ContactMessageSerializer,
    ContactMessageCreateSerializer,
    ContactMessageAdminSerializer,
    ImpactStatisticSerializer,
    ContactInfoSerializer,
)
from accounts.permissions import AdminBypassPermission
from ..services import ImpactStatsService


class IsAdmin(AdminBypassPermission):

    def has_regular_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff


class ContactMessageCreateView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Contact Messages"],
        summary="Submit a contact message",
        description="Public endpoint to submit contact messages from the website",
        request=ContactMessageCreateSerializer,
        responses={
            201: ContactMessageSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        serializer = ContactMessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            contact_message = serializer.save()
            response_serializer = ContactMessageSerializer(contact_message)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        tags=["Contact Messages"],
        summary="List all contact messages",
        description="Retrieve all contact messages. Accessible only to admin users.",
        responses={
            200: ContactMessageAdminSerializer(many=True),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    retrieve=extend_schema(
        tags=["Contact Messages"],
        summary="Retrieve contact message",
        description="Retrieve a single contact message by ID.",
        responses={
            200: ContactMessageAdminSerializer,
            404: OpenApiResponse(description="Not found"),
        },
    ),
    update=extend_schema(
        tags=["Contact Messages"],
        summary="Update contact message",
        description="Update a contact message (admin notes, status, etc.)",
        request=ContactMessageAdminSerializer,
        responses={
            200: ContactMessageAdminSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    partial_update=extend_schema(
        tags=["Contact Messages"],
        summary="Partially update contact message",
        description="Partially update a contact message.",
        request=ContactMessageAdminSerializer,
        responses={
            200: ContactMessageAdminSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    destroy=extend_schema(
        tags=["Contact Messages"],
        summary="Delete contact message",
        description="Delete a contact message.",
        responses={
            204: OpenApiResponse(description="Deleted successfully"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
)
class ContactMessageViewSet(viewsets.ModelViewSet):
    
    queryset = ContactMessage.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
            return ContactMessageAdminSerializer
        return ContactMessageSerializer

    def get_permissions(self):

        if self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
            return [IsAdmin()]
        return [AllowAny()]

    @action(detail=False, methods=["get"], permission_classes=[IsAdmin])
    def pending(self, request):
        pending_messages = ContactMessage.objects.filter(
            status=ContactMessage.PENDING
        )
        serializer = self.get_serializer(pending_messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def mark_as_viewed(self, request, pk=None):
        
        contact_message = self.get_object()
        contact_message.status = ContactMessage.VIEWED
        contact_message.save()
        serializer = self.get_serializer(contact_message)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def mark_as_responded(self, request, pk=None):
       
        contact_message = self.get_object()
        contact_message.status = ContactMessage.RESPONDED
        if "admin_notes" in request.data:
            contact_message.admin_notes = request.data["admin_notes"]
        contact_message.save()
        serializer = self.get_serializer(contact_message)
        return Response(serializer.data)


class ImpactStatisticListView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=["Impact Statistics"],
        summary="Get all impact statistics",
        description="Retrieve all active impact statistics displayed on the home page. Public endpoint.",
        responses={
            200: ImpactStatisticSerializer(many=True),
        },
    )
    def get(self, request):
       
        try:
            ImpactStatsService.update_statistics()
        except Exception as e:
          
            print(f"Error updating impact statistics: {e}")
       
        statistics = ImpactStatistic.objects.filter(is_active=True)
        serializer = ImpactStatisticSerializer(statistics, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=["Impact Statistics"],
        summary="List all impact statistics",
        description="Retrieve all impact statistics (admin only)",
        responses={200: ImpactStatisticSerializer(many=True)},
    ),
    create=extend_schema(
        tags=["Impact Statistics"],
        summary="Create impact statistic",
        description="Create a new impact statistic (admin only)",
        request=ImpactStatisticSerializer,
        responses={201: ImpactStatisticSerializer},
    ),
    retrieve=extend_schema(
        tags=["Impact Statistics"],
        summary="Retrieve impact statistic",
        description="Retrieve a single impact statistic by ID (admin only)",
        responses={200: ImpactStatisticSerializer},
    ),
    update=extend_schema(
        tags=["Impact Statistics"],
        summary="Update impact statistic",
        description="Update an impact statistic (admin only)",
        request=ImpactStatisticSerializer,
        responses={200: ImpactStatisticSerializer},
    ),
    partial_update=extend_schema(
        tags=["Impact Statistics"],
        summary="Partially update impact statistic",
        description="Partially update an impact statistic (admin only)",
        request=ImpactStatisticSerializer,
        responses={200: ImpactStatisticSerializer},
    ),
    destroy=extend_schema(
        tags=["Impact Statistics"],
        summary="Delete impact statistic",
        description="Delete an impact statistic (admin only)",
        responses={204: OpenApiResponse(description="Deleted successfully")},
    ),
)
class ImpactStatisticViewSet(viewsets.ModelViewSet):
 
    
    queryset = ImpactStatistic.objects.all()
    serializer_class = ImpactStatisticSerializer
    permission_classes = [IsAdmin]


class ContactInfoListView(APIView):
  
    
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=["Contact Info"],
        summary="Get contact information",
        description="Retrieve the business contact information displayed on the Get in Touch page. Public endpoint.",
        responses={
            200: ContactInfoSerializer,
        },
    )
    def get(self, request):
      
        contact_info = ContactInfo.objects.filter(is_active=True).first()
        if contact_info:
            serializer = ContactInfoSerializer(contact_info)
            return Response(serializer.data)
        return Response({"error": "Contact information not available"}, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    list=extend_schema(
        tags=["Contact Info"],
        summary="List contact information",
        description="Retrieve all contact information entries (admin only)",
        responses={200: ContactInfoSerializer(many=True)},
    ),
    create=extend_schema(
        tags=["Contact Info"],
        summary="Create contact information",
        description="Create a new contact information entry (admin only)",
        request=ContactInfoSerializer,
        responses={201: ContactInfoSerializer},
    ),
    retrieve=extend_schema(
        tags=["Contact Info"],
        summary="Retrieve contact information",
        description="Retrieve a single contact information entry by ID (admin only)",
        responses={200: ContactInfoSerializer},
    ),
    update=extend_schema(
        tags=["Contact Info"],
        summary="Update contact information",
        description="Update contact information (admin only)",
        request=ContactInfoSerializer,
        responses={200: ContactInfoSerializer},
    ),
    partial_update=extend_schema(
        tags=["Contact Info"],
        summary="Partially update contact information",
        description="Partially update contact information (admin only)",
        request=ContactInfoSerializer,
        responses={200: ContactInfoSerializer},
    ),
    destroy=extend_schema(
        tags=["Contact Info"],
        summary="Delete contact information",
        description="Delete contact information (admin only)",
        responses={204: OpenApiResponse(description="Deleted successfully")},
    ),
)
class ContactInfoViewSet(viewsets.ModelViewSet):

    
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer
    permission_classes = [IsAdmin]
