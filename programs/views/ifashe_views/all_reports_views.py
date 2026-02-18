from django.http import FileResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsIfasheManager
from utils.reports.ifashe.family_reports import (
    FamilyOverviewExcelReport,
    FamilyOverviewPDFReport,
)
from utils.reports.ifashe.parents_work_reports import (
    ParentWorkCompliancePDFReport,
    ParentWorkExcelReport,
)
from utils.reports.ifashe.summary_reports import (
    IFASHESummaryPDFReport,
    IfasheSummaryExcelReport,
)
from utils.reports.ifashe.helpers import safe_filename
from utils.reports.ifashe.supports_reports import (
    # ChildSupportExcelReport,
    ChildSupportPDFReport,
    SupportExcelReport,
)
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes


class IfasheSummaryPDFReportView(APIView):
    permission_classes = [IsAuthenticated, IsIfasheManager]

    @extend_schema(
        tags=["IfasheTugufashe Program"],
        description="Generates the IFASHE Global Summary Report in PDF format.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        filename = safe_filename("ifashe_summary_report", "pdf")
        path = f"/tmp/{filename}"

        report = IFASHESummaryPDFReport(path)
        report.generate()

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )


class IfasheSummaryExcelReportView(APIView):
    permission_classes = [IsAuthenticated, IsIfasheManager]

    @extend_schema(
        tags=["IfasheTugufashe Program"],
        description="Generates the IFASHE TUGUFASHE Global Summary Report in Excel format.",
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        filename = safe_filename("ifashe_summary_report", "xlsx")
        path = f"/tmp/{filename}"

        report = IfasheSummaryExcelReport()
        report.generate(path)

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


class IfasheSupportPDFReportView(APIView):
    permission_classes = [IsAuthenticated, IsIfasheManager]

    @extend_schema(
        description="Generates the IFASHE Support Report (School + Clothes) in PDF format.",
        tags=["IfasheTugufashe Program"],
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        filename = safe_filename("ifashe_support_report", "pdf")
        path = f"/tmp/{filename}"

        report = ChildSupportPDFReport(path)
        report.generate()

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )


class IfasheSupportExcelReportView(APIView):
    permission_classes = [IsAuthenticated, IsIfasheManager]

    @extend_schema(
        description="Generates the IFASHE Support Report (School + Clothes) in Excel format.",
        tags=["IfasheTugufashe Program"],
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        filename = safe_filename("ifashe_support_report", "xlsx")
        path = f"/tmp/{filename}"

        report = SupportExcelReport()
        report.generate(path)

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


class ParentWorkPDFReportView(APIView):
    permission_classes = [IsAuthenticated, IsIfasheManager]

    @extend_schema(
        description="Generates the Parent Work Requirement Report in PDF format.",
        tags=["IfasheTugufashe Program"],
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        filename = safe_filename("ifashe_parent_work_report", "pdf")
        path = f"/tmp/{filename}"

        report = ParentWorkCompliancePDFReport(path)
        report.generate()

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )


class ParentWorkExcelReportView(APIView):
    permission_classes = [IsAuthenticated, IsIfasheManager]

    @extend_schema(
        description="Generates the Parent Work Requirement Report in Excel format.",
        tags=["IfasheTugufashe Program"],
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        filename = safe_filename("ifashe_parent_work_report", "xlsx")
        path = f"/tmp/{filename}"

        report = ParentWorkExcelReport()
        report.generate(path)

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


class FamilyOverviewPDFReportView(APIView):
    permission_classes = [IsAuthenticated, IsIfasheManager]

    @extend_schema(
        description="Generates the Family Overview Report in PDF format.",
        tags=["IfasheTugufashe Program"],
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        filename = safe_filename("ifashe_family_overview", "pdf")
        path = f"/tmp/{filename}"

        report = FamilyOverviewPDFReport(path)
        report.generate()

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/pdf",
        )


class FamilyOverviewExcelReportView(APIView):
    permission_classes = [IsAuthenticated, IsIfasheManager]

    @extend_schema(
        description="Generates the Family Overview Report in Excel format.",
        tags=["IfasheTugufashe Program"],
        responses={200: OpenApiTypes.BINARY},
    )
    def get(self, request):
        filename = safe_filename("ifashe_family_overview", "xlsx")
        path = f"/tmp/{filename}"

        report = FamilyOverviewExcelReport()
        report.generate(path)

        return FileResponse(
            open(path, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
