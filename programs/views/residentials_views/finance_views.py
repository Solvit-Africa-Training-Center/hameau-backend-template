from rest_framework import viewsets, filters 
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import ResidentialFinancialPlan
from programs.serializers import ResidentialFinancialPlanSerializer
from accounts.permissions import IsResidentialManager
from utils.paginators import StandardResultsSetPagination

class ResidentialFinanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Residential Financial Plans.
    """
    queryset = ResidentialFinancialPlan.objects.all().select_related('child')
    serializer_class = ResidentialFinancialPlanSerializer
    permission_classes = [IsAuthenticated, IsResidentialManager]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['child', 'month', 'year']
    search_fields = ['child__first_name', 'child__last_name', 'notes']
    ordering_fields = ['month', 'year', 'total_cost']
    ordering = ['-year', '-month']
    pagination_class = StandardResultsSetPagination
