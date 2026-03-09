from rest_framework import viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema

from website_content.serializers.company_info_serializers import CompanyInfoSerializer
from website_content.models.company_info_models import CompanyInfo

@extend_schema(tags=["Company Info"])
class CompanyInfoCreateView(viewsets.ModelViewSet):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()
    