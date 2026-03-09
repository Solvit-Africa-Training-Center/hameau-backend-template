from rest_framework import viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema

from website_content.serializers.we_are_serializers import WeAreSerializer
from website_content.models.we_are_models import WeAre


@extend_schema(tags=["Who we are"])
class WeAreCreateView(viewsets.ModelViewSet):
    queryset = WeAre.objects.all()
    serializer_class = WeAreSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()