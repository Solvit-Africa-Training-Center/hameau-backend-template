from rest_framework import viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema

from website_content.serializers.company_info_serializers import CompanyInfoSerializer, SocialMediaSerializer, WorkingDaysHoursSerializer
from website_content.models.company_info_models import CompanyInfo, SocialMedia, WorkingDaysHours

@extend_schema(tags=["Company Info"])
class CompanyInfoCreateView(viewsets.ModelViewSet):
    queryset = CompanyInfo.objects.all()
    serializer_class = CompanyInfoSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()


@extend_schema(tags=["Company Social media"])
class SocialMediaCreateView(viewsets.ModelViewSet):
    queryset = SocialMedia.objects.all()
    serializer_class = SocialMediaSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()

@extend_schema(tags=["Company Working Days Hours"])
class WorkingDaysHoursCreateView(viewsets.ModelViewSet):
    queryset = WorkingDaysHours.objects.all()
    serializer_class = WorkingDaysHoursSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()
    