from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import Parent
from programs.serializers.ifashe_serializers import IfasheParentSerializer
from accounts.permissions import IsIfasheManager


class IfasheParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all().select_related('family')
    serializer_class = IfasheParentSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'relationship', 'marital_status']
    search_fields = ['first_name', 'last_name', 'national_id', 'phone']
    ordering_fields = ['created_on', 'first_name', 'last_name']
    ordering = ['-created_on']
