from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from public_modules.serializers.contact_serializers import ContactMessageSerializer


@extend_schema(tags=["Public Modules"])
class ContactMessageCreateView(generics.CreateAPIView):
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
