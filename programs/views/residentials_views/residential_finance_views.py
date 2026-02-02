from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg
from decimal import Decimal

from programs.models import HealthRecord, ChildEducation, ResidentialFinancialPlan, ChildInsurance, Child
from programs.serializers import (
    SpendingReportSerializer,
    CostReportSerializer,
)
from accounts.permissions import IsResidentialManager


class ResidentialFinanceViewSet(viewsets.ViewSet):
    """
    ViewSet for managing residential program finances.
    Handles spending summaries and cost reports.
    """
    permission_classes = [IsAuthenticated, IsResidentialManager]

    @action(detail=False, methods=['get'])
    def spending_summary(self, request):
        """
        Get spending summary for:
        - Normal spending (kids without special diets)
        - Special diet spending (kids with special diets)
        - Education spending
        """
        return Response(
            {
                'success': True,
                'data': SpendingReportSerializer({}, context={'request': request}).data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def cost_report(self, request):
        """Generate a detailed cost report"""
        return Response(
            {
                'success': True,
                'data': CostReportSerializer({}, context={'request': request}).data
            },
            status=status.HTTP_200_OK
        )
