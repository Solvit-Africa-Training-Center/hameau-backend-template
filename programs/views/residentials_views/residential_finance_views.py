from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg
from decimal import Decimal

from programs.models import HealthRecord, ChildEducation, ResidentialFinancialPlan, ChildInsurance, Child
from programs.serializers import (
    SpendingReportSerializer,
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
        queryset = HealthRecord.objects.all()
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(visit_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(visit_date__lte=date_to)
        
        total_cost = queryset.aggregate(total=Sum('cost'))['total'] or Decimal('0.00')
        
        cost_by_type = queryset.values('record_type').annotate(
            total_cost=Sum('cost'),
            count=Count('id'),
            average_cost=Avg('cost')
        ).order_by('-total_cost')
        
        cost_by_child = queryset.values(
            'child__id', 'child__first_name', 'child__last_name'
        ).annotate(
            total_cost=Sum('cost'),
            record_count=Count('id')
        ).order_by('-total_cost')[:10]
        
        monthly_costs = queryset.extra(
            select={'month': 'EXTRACT(month FROM visit_date)', 'year': 'EXTRACT(year FROM visit_date)'}
        ).values('year', 'month').annotate(
            total_cost=Sum('cost'),
            count=Count('id')
        ).order_by('year', 'month')
        
        return Response(
            {
                'success': True,
                'date_range': {
                    'from': date_from,
                    'to': date_to
                },
                'total_cost': float(total_cost),
                'cost_by_type': [
                    {
                        'record_type': item['record_type'],
                        'total_cost': float(item['total_cost'] or 0),
                        'count': item['count'],
                        'average_cost': float(item['average_cost'] or 0),
                    }
                    for item in cost_by_type
                ],
                'top_10_children_by_cost': [
                    {
                        'child_id': str(item['child__id']),
                        'child_name': f"{item['child__first_name']} {item['child__last_name']}",
                        'total_cost': float(item['total_cost'] or 0),
                        'record_count': item['record_count'],
                    }
                    for item in cost_by_child
                ],
                'monthly_breakdown': [
                    {
                        'year': int(item['year']),
                        'month': int(item['month']),
                        'total_cost': float(item['total_cost'] or 0),
                        'count': item['count'],
                    }
                    for item in monthly_costs
                ]
            },
            status=status.HTTP_200_OK
        )
