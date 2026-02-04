from rest_framework import viewsets, filters, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import Family
from programs.serializers.ifashe_serializers import IfasheFamilySerializer
from utils.reports import ExcelRenderer

from accounts.permissions import IsIfasheManager, IsSystemAdmin


class IfasheFamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.all().prefetch_related('parents', 'children')
    serializer_class = IfasheFamilySerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['province', 'district', 'sector', 'vulnerability_level', 'housing_condition']
    search_fields = ['family_name', 'family_id', 'address']
    ordering_fields = ['created_on', 'family_name', 'vulnerability_level']
    ordering = ['-created_on']
