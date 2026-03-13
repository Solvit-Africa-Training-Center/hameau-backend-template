from rest_framework import viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema

from website_content.serializers.company_info_serializers import CompanyInfoSerializer, SocialMediaSerializer, WorkingDaysHoursSerializer
from website_content.models.company_info_models import CompanyInfo, SocialMedia, WorkingDaysHours
from rest_framework.response import Response

@extend_schema(tags=["Company Info"])
class CompanyInfoCreateView(viewsets.ModelViewSet):
    queryset = CompanyInfo.objects.last()
    serializer_class = CompanyInfoSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        serializers=CompanyInfoSerializer(self.get_queryset())
        return Response(serializers.data)
        


@extend_schema(tags=["Company Social media"])
class SocialMediaCreateView(viewsets.ModelViewSet):
    queryset = SocialMedia.objects.last()
    serializer_class = SocialMediaSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        serializers=SocialMediaSerializer(self.get_queryset())
        return Response(serializers.data)

@extend_schema(tags=["Company Working Days Hours"])
class WorkingDaysHoursCreateView(viewsets.ModelViewSet):
    queryset = WorkingDaysHours.objects.last()
    serializer_class = WorkingDaysHoursSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        serializers=WorkingDaysHoursSerializer(self.get_queryset())
        return Response(serializers.data)
    