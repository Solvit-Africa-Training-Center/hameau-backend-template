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
from drf_spectacular.types import OpenApiTypes


logger = logging.getLogger(__name__)


@extend_schema_view(
    spending_summary=extend_schema(tags=["Residential Care Program"]),
    cost_report=extend_schema(tags=["Residential Care Program"]),
)
class ResidentialFinanceViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsResidentialManager]
    serializer_class = SpendingReportSerializer

    @extend_schema(
        responses=SpendingReportSerializer,
        description="""
        Returns spending summary including:
        - Normal spending
        - Special diet spending
        - Education spending
        """,
    )
    @action(detail=False, methods=["get"], url_path="spending-summary")
    def spending_summary(self, request):
        logger.info(
            f"Financial report accessed by user {request.user.id} ({request.user.email})"
        )

        serializer = SpendingReportSerializer({}, context={"request": request})

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses=CostReportSerializer,
        description="Returns detailed residential cost report",
    )
    @action(detail=False, methods=["get"], url_path="cost-report")
    def cost_report(self, request):
        serializer = CostReportSerializer({}, context={"request": request})

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Residential Care Program"],
    description="Generates a PDF report summarizing residential financial data.",
    responses={200: OpenApiTypes.BINARY},
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
    tags=["Residential Care Program"],
    description="Generates an Excel report summarizing residential financial data.",
    responses={200: OpenApiTypes.BINARY},
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
