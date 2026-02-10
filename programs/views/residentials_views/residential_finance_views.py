import logging

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
    FinancialReportDataSerializer,
)
from accounts.permissions import IsResidentialManager
from rest_framework import viewsets, status, renderers
from utils.reports import PDFRenderer, ExcelRenderer

logger = logging.getLogger(__name__)

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

    @action(detail=False, methods=['get'], renderer_classes=[renderers.JSONRenderer, PDFRenderer, ExcelRenderer])
    def download_report(self, request):
        """
        Download financial report as PDF or Excel.
        Query params:
        - format: 'pdf', 'excel', or 'json' (default: 'json')
        - report_type: 'spending' or 'cost' (default: 'spending')
        - date_from, date_to: Date filters
        """
        report_type = request.query_params.get('report_type', 'spending')
        
        filename = f"financial_report_{report_type}"
        data = []
        title = "Financial Report"
        date_range = {}

        if report_type == 'cost':
             serializer = CostReportSerializer({}, context={'request': request})
             report_data = serializer.data
             title = f"Cost Report ({report_data['date_range']['from']} - {report_data['date_range']['to']})"
             date_range = report_data['date_range']
             
             for item in report_data['cost_by_type']:
                 data.append({
                     "Record Type": item['record_type'],
                     "Count": item['count'],
                     "Total Cost": f"{item['total_cost']:.2f}",
                     "Avg Cost": f"{item['average_cost']:.2f}"
                 })
                 
        else: # spending
             serializer = SpendingReportSerializer({}, context={'request': request})
             report_data = serializer.data
             title = "Spending Summary"
             
             data = [
                 {"Category": "Normal Spending", "Amount": f"{report_data['normal_spending']:.2f}"},
                 {"Category": "Special Diet Spending", "Amount": f"{report_data['special_diet_spending']:.2f}"},
                 {"Category": "Education Spending", "Amount": f"{report_data['education_spending']:.2f}"},
                 {"Category": "Total Spending", "Amount": f"{report_data['total_spending']:.2f}"},
             ]

        report_context = {
            "report_type": report_type,
            "title": title,
            "filename": filename,
            "data": data,
            "date_range": date_range
        }
        
        serializer = FinancialReportDataSerializer(report_context)
        return Response(serializer.data)
