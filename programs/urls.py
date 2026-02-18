from rest_framework.routers import DefaultRouter
from django.urls import path


from .views import (
    ParentAttendanceViewSet,
    ParentPerformanceViewSet,
    ParentWorkContractViewSet,
    ChildViewSet,
    ChildProgressViewSet,
    EducationInstitutionViewSet,
    EducationProgramViewSet,
    ChildEducationViewSet,
    CaretakerViewSet,
    DressingDistributionViewSet,
    HealthRecordViewSet,
    ResidentialFinanceViewSet,
    IfasheFamilyViewSet,
    IfasheChildViewSet,
    IfasheParentViewSet,
    SponsorshipViewSet,
    SchoolSupportViewSet,
    FamilyOverviewPDFReportView,
    FamilyOverviewExcelReportView,
    IfasheSummaryPDFReportView,
    IfasheSummaryExcelReportView,
    IfasheSupportPDFReportView,
    IfasheSupportExcelReportView,
    ParentWorkPDFReportView,
    ParentWorkExcelReportView,
    ResidentialFinanceExcelReportView,
    ResidentialFinancePDFReportView,
    InternshipApplicationViewSet,
    ChildCaretakerAssignmentViewSet
)

router = DefaultRouter()

router.register("children", ChildViewSet, basename="child")
router.register("children_progress", ChildProgressViewSet, basename="progress")
router.register(
    "children_educational_institutions",
    EducationInstitutionViewSet,
    basename="-residential-care-institution",
)
router.register("children-caretaker",ChildCaretakerAssignmentViewSet, basename="children_caretaker")
router.register(
    "children_educational_programs", EducationProgramViewSet, basename="program"
)
router.register(
    "children_programs_enrollments", ChildEducationViewSet, basename="enrollment"
)
router.register("caretakers", CaretakerViewSet, basename="caretaker")
router.register("health-records", HealthRecordViewSet, basename="health-record")
router.register(
    "residential-finance", ResidentialFinanceViewSet, basename="residential-finance"
)
router.register("ifashe-families", IfasheFamilyViewSet, basename="ifashe-family")
router.register("ifashe-children", IfasheChildViewSet, basename="ifashe-child")
router.register("ifashe-parents", IfasheParentViewSet, basename="ifashe-parent")
router.register(
    "ifashe-sponsorships", SponsorshipViewSet, basename="ifashe-sponsorship"
)
router.register(
    "ifashe-school-support", SchoolSupportViewSet, basename="ifashe-school-support"
)
router.register(
    "ifashe-dressing-distributions",
    DressingDistributionViewSet,
    basename="ifashe-dressing-distributions",
)
router.register(
    "ifashe-parent-contracts",
    ParentWorkContractViewSet,
    basename="ifashe-parent-contracts",
)
router.register(
    "ifashe-parent-attendance",
    ParentAttendanceViewSet,
    basename="ifashe-parent-attendance",
)
router.register(
    "ifashe-parent-performance",
    ParentPerformanceViewSet,
    basename="ifashe-parent-performance",
)
router.register(
    "internship-applications",
    InternshipApplicationViewSet,
    basename="internship-application",
)

urlpatterns = router.urls


urlpatterns += [
    path(
        "ifashe/reports/families/pdf/",
        FamilyOverviewPDFReportView.as_view(),
        name="ifashe-family-overview-pdf",
    ),
    path(
        "ifashe/reports/families/excel/",
        FamilyOverviewExcelReportView.as_view(),
        name="ifashe-family-overview-excel",
    ),
    path(
        "ifashe/reports/summary/pdf/",
        IfasheSummaryPDFReportView.as_view(),
        name="ifashe-summary-pdf",
    ),
    path(
        "ifashe/reports/summary/excel/",
        IfasheSummaryExcelReportView.as_view(),
        name="ifashe-summary-excel",
    ),
    path(
        "ifashe/reports/support/pdf/",
        IfasheSupportPDFReportView.as_view(),
        name="ifashe-support-pdf",
    ),
    path(
        "ifashe/reports/support/excel/",
        IfasheSupportExcelReportView.as_view(),
        name="ifashe-support-excel",
    ),
    path(
        "ifashe/reports/parent-work/pdf/",
        ParentWorkPDFReportView.as_view(),
        name="ifashe-parent-work-pdf",
    ),
    path(
        "ifashe/reports/parent-work/excel/",
        ParentWorkExcelReportView.as_view(),
        name="ifashe-parent-work-excel",
    ),
    path(
        "residential-finance/pdf-report/",
        ResidentialFinancePDFReportView.as_view(),
        name="residential-finance-pdf-report",
    ),
    path(
        "residential-finance/excel-report/",
        ResidentialFinanceExcelReportView.as_view(),
        name="residential-finance-excel-report",
    ),
]
