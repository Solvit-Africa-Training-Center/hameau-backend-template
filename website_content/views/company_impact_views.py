from rest_framework import viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema

from website_content.serializers.company_impact_serializers import CompanyImpactSerializer
from website_content.models.company_impact_models import CompanyImpact

@extend_schema(tags=["Company Impact"])
class CompanyImpactCreateView(viewsets.ModelViewSet):
    queryset = CompanyImpact.objects.all()
    serializer_class = CompanyImpactSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()