import logging
from django.contrib.auth import authenticate

from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend


from .models import User, ActivityLog, record_activity
from .permissions import (
    CanDestroyManager,
    IsSystemAdmin,
)
from .serializers import (
    LogoutSerializer,
    ManagerSerializer,
    LoginSerializer,
    RequestPasswordResetSerializer,
    ResetPasswordConfirmSerializer,
    ChangePasswordSerializer,
    ActivityLogSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        tags=["Activity Logs"],
        summary="List activity logs",
        description="Retrieve a list of all system activities. Accessible only to system administrators.",
        responses={
            200: ActivityLogSerializer(many=True),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    retrieve=extend_schema(
        tags=["Activity Logs"],
        summary="Retrieve activity log",
        description="Retrieve a single activity log by ID.",
        responses={
            200: ActivityLogSerializer,
            404: OpenApiResponse(description="Not found"),
        },
    ),
)
class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all().select_related("user")
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated, IsSystemAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["user", "action", "resource"]
    search_fields = ["action", "resource", "resource_id", "details"]
    ordering_fields = ["timestamp"]
    ordering = ["-timestamp"]

@extend_schema_view(
    list=extend_schema(
        tags=["Managers"],
        summary="List managers",
        description="Retrieve a list of all managers. Accessible only to system administrators.",
        responses={
            200: ManagerSerializer(many=True),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    retrieve=extend_schema(
        tags=["Managers"],
        summary="Retrieve manager",
        description="Retrieve a single manager by ID.",
        responses={
            200: ManagerSerializer,
            404: OpenApiResponse(description="Not found"),
        },
    ),
    create=extend_schema(
        tags=["Managers"],
        summary="Create manager",
        description="Create a new manager account. Accessible only to system administrators.",
        request=ManagerSerializer,
        responses={
            201: ManagerSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    update=extend_schema(
        tags=["Managers"],
        summary="Update manager",
        description="Update a manager's details.",
        request=ManagerSerializer,
        responses={
            200: ManagerSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    partial_update=extend_schema(
        tags=["Managers"],
        summary="Partially update manager",
        description="Partially update a manager's details.",
        request=ManagerSerializer,
        responses={
            200: ManagerSerializer,
            400: OpenApiResponse(description="Validation error"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
    destroy=extend_schema(
        tags=["Managers"],
        summary="Delete manager",
        description="Delete a manager account. Requires destroy permissions.",
        responses={
            204: OpenApiResponse(description="Deleted successfully"),
            403: OpenApiResponse(description="Permission denied"),
        },
    ),
)
class ManagerViewset(viewsets.ModelViewSet):
    serializer_class = ManagerSerializer
    queryset = User.objects.order_by("first_name")
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsSystemAdmin()]
        elif self.action == "list":
            return [IsSystemAdmin()]
        elif self.action == "destroy":
            return [CanDestroyManager()]
        return super().get_permissions()

    @extend_schema(
        tags=["Managers"],
        summary="List only managers",
        description=(
            "Retrieve a list of program managers only. "
            "System administrators are excluded from the response."
        ),
        responses={
            200: ManagerSerializer(many=True),
            403: OpenApiResponse(description="Permission denied"),
        },
    )
    @action(methods=["get"], detail=False)
    def only_managers(self, request):
        """
        Listing of Program Managers.
        System administrators are excluded.
        """
        queryset = User.objects.order_by("first_name").exclude(role=User.ADMIN)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for manager authentication (login).

    This endpoint:
    - Validates user credentials
    - Authenticates the user
    - Returns authentication data (tokens, user info)

    No authentication is required because this is the login endpoint.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login Manager",
        description="Authenticates a manager and returns access/refresh tokens with user details.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(
                description="Login successful",
                response={
                    "type": "object",
                    "properties": {
                        "access": {"type": "string"},
                        "refresh": {"type": "string"},
                        "user": {"type": "object"},
                    },
                },
            ),
            400: OpenApiResponse(description="Invalid credentials or validation error"),
        },
        tags=["Authentication of Managers"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Record activity after successful authentication
        try:
            user = User.objects.get(email=request.data.get("email"))
            record_activity(
                request, 
                action="LOGIN", 
                user=user,
                resource="User", 
                resource_id=str(user.id),
                details={"email": user.email}
            )
        except User.DoesNotExist:
            pass

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Authentication of Managers"],
    request=RequestPasswordResetSerializer,
    responses={
        200: OpenApiResponse(description="Password reset code sent successfully"),
        400: OpenApiResponse(description="Validation error"),
    },
    summary="Request password reset",
    description="Sends a password reset code to the manager's email address.",
)
class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        logger.info("Initializing user password request")
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.success("Succefully sent the code to the user email")
        return Response(
            {"message": "Password reset code sent to your email"},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Authentication of Managers"],
    request=ResetPasswordConfirmSerializer,
    responses={
        200: OpenApiResponse(description="Password reset successfully"),
        400: OpenApiResponse(description="Invalid or expired reset code"),
    },
    summary="Confirm password reset",
    description="Resets the manager's password using the provided reset code.",
)
class ResetPasswordConfirmView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Password reset successfully")

        return Response(
            {"message": "Password reset successfully"}, status=status.HTTP_200_OK
        )


@extend_schema(
    tags=["Authentication of Managers"],
    request=LogoutSerializer,
    responses={
        204: OpenApiResponse(description="Logged out successfully"),
        400: OpenApiResponse(description="Invalid token"),
    },
    summary="Logout",
    description="Logs out the authenticated user by invalidating their token.",
)
class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["Authentication of Managers"],
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(description="Password changed successfully"),
        400: OpenApiResponse(description="Validation error"),
        401: OpenApiResponse(description="Authentication required"),
    },
    summary="Change password",
    description="Allows an authenticated user to change their password.",
)
class ChangePasswordView(APIView):
    """
    API endpoint for changing user password.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        logger.success("Password changed successfully")
        serializer.save()
        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )
