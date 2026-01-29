from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated


from accounts.models import User
from .permissions import (
    IsIfasheManager,
    IsInternshipManager,
    IsOwner,
    CanDestroyManager,
    IsResidentialManager,
    IsSystemAdmin,
)
from .serializers import ManagerSerializer, LoginSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
            return [(CanDestroyManager())]
        return super().get_permissions()

    @action(methods=["get"], detail=False)
    def only_managers(self, request):
        """
        Listing of Program Mangers
        We excluded the system admins
        """
        queryset = User.objects.order_by("first_name").exclude(role=User.ADMIN)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User created successfully, credentials are sent to the email",
                "email": user.email,
                "phone_number": user.phone,
            },
            status=status.HTTP_201_CREATED,
        )


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

    @swagger_auto_schema(
        operation_summary="managers_login",
        operation_description=(
            "Authenticates a user using their credentials.\n\n"
            "On successful authentication, the API returns authentication-related data, "
            "such as access and refresh tokens and serialized user details, "
            "id, email, first_name, last_name and role.\n\n"
            "If the credentials are invalid, a validation error is returned."
        ),
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        ),
                        "refresh": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        ),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Authenticated user details",
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Invalid credentials or validation error"
            ),
        },
        tags=["managers"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )
