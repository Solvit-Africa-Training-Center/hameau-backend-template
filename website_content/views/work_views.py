from rest_framework import viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema

from website_content.serializers.work_serializers import WorkSerializer
from website_content.models.work_models import Work


@extend_schema(tags=["Works"])
class WorkCreateView(viewsets.ModelViewSet):
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()
