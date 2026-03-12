from rest_framework import viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema
from website_content.models.contact_us_models import ContactMessage
from website_content.serializers.contact_us_serializers import ContactMessageSerializer


@extend_schema(tags=["Contact Us"])
class ContactMessageCreateView(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return super().get_permissions()