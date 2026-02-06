from rest_framework import viewsets, filters, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import SponsoredChild, DressingDistribution
from programs.serializers.ifashe_serializers import IfasheChildSerializer, DressingDistributionSerializer
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


class DressingDistributionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clothes Support / Dressing Distribution.
    """
    queryset = DressingDistribution.objects.all().select_related('child')
    serializer_class = DressingDistributionSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['child', 'item_type', 'distribution_date']
    search_fields = ['child__first_name', 'child__last_name', 'item_type', 'notes']
    ordering_fields = ['distribution_date', 'quantity']
    ordering = ['-distribution_date']
