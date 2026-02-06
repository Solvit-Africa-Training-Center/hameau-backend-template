from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import SchoolSupport
from programs.serializers.ifashe_serializers import SchoolSupportSerializer
from accounts.permissions import IsIfasheManager

class SchoolSupportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing School Support (Fees & Materials).
    """
    queryset = SchoolSupport.objects.all().select_related('child', 'school')
    serializer_class = SchoolSupportSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['child', 'school', 'academic_year', 'payment_status']
    search_fields = ['child__first_name', 'child__last_name', 'school__name', 'notes']
    ordering_fields = ['academic_year', 'school_fees']
    ordering = ['-academic_year']
