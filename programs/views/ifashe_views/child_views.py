from rest_framework import viewsets, filters, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import SponsoredChild
from programs.serializers.ifashe_serializers import IfasheChildSerializer
from utils.reports import ExcelRenderer


from accounts.permissions import IsIfasheManager

class IfasheChildViewSet(viewsets.ModelViewSet):
    queryset = SponsoredChild.objects.all().select_related('family')
    serializer_class = IfasheChildSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school_name', 'school_level', 'support_status', 'gender']
    search_fields = ['first_name', 'last_name', 'family__family_name']
    ordering_fields = ['created_on', 'first_name', 'last_name', 'date_of_birth']
    ordering = ['-created_on']
