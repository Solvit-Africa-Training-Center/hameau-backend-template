from datetime import timezone
from django.http import FileResponse
from rest_framework.views import APIView
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from programs.serializers import (
    SpendingReportSerializer,
    CostReportSerializer,
)
from accounts.permissions import IsResidentialManager
from utils.reports.residentials.spending_summary import (
    SpendingSummaryExcelReport,
    SpendingSummaryPDFReport,
)
from utils.reports.ifashe.helpers import safe_filename
from drf_spectacular.utils import extend_schema, extend_schema_view

logger = logging.getLogger(__name__)

@extend_schema_view(
    spending_summary=extend_schema(tags=["Residential Care Program - Finance"]),
    cost_report=extend_schema(tags=["Residential Care Program - Finance"]),
    download_report=extend_schema(tags=["Residential Care Program - Finance"]),
)
class ResidentialFinanceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsResidentialManager]

    @action(detail=False, methods=["get"])
    def spending_summary(self, request):
        """
        Get spending summary for:
        - Normal spending (kids without special diets)
        - Special diet spending (kids with special diets)
        - Education spending
        """

        logger.info(
        f"Financial report accessed by user {request.user.id} ({request.user.email})"
        )

        return Response(
            {
                "success": True,
                "data": SpendingReportSerializer({}, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"])
    def cost_report(self, request):
        """Generate a detailed cost report"""
        return Response(
            {
                "success": True,
                "data": CostReportSerializer({}, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Residential Care Program - Finance"],
    description="Generates a PDF report summarizing residential financial data.",
)
class ResidentialFinancePDFReportView(APIView):
    permission_classes = [IsAuthenticated, IsResidentialManager]

    def get(self, request):
        logger.info(
        f"PDF financial report downloaded by user {request.user.id} at {timezone.now()}"
        )
        filename = safe_filename("residential_financial_report", "pdf")
        path = f"/tmp/{filename}"

        report = SpendingSummaryPDFReport(path, request=request)
        report.generate()

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )


@extend_schema(
    tags=["Residential Care Program - Finance"],
    description="Generates an Excel report summarizing residential financial data.",
)
class ResidentialFinanceExcelReportView(APIView):
    permission_classes = [IsAuthenticated, IsResidentialManager]

    def get(self, request):
        filename = safe_filename("residential_financial_report", "xlsx")
        path = f"/tmp/{filename}"

        report = SpendingSummaryExcelReport(request=request)
        report.generate(path)

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
