# Residentials Views
from programs.views.residentials_views.child_views import (
    ChildViewSet,
    ChildProgressViewSet,
    EducationInstitutionViewSet,
    EducationProgramViewSet,
    ChildEducationViewSet,
)

from programs.views.residentials_views.childcaretaker import (
    ChildCaretakerAssignmentViewSet,
)

from programs.views.residentials_views.caretaker_views import CaretakerViewSet
from programs.views.residentials_views.health_record_views import HealthRecordViewSet
from programs.views.residentials_views.residential_finance_views import (
    ResidentialFinanceViewSet,
    ResidentialFinanceExcelReportView,
    ResidentialFinancePDFReportView,
)

# Ifashe Views
from programs.views.ifashe_views.family_views import IfasheFamilyViewSet
from programs.views.ifashe_views.child_views import (
    IfasheChildViewSet,
    DressingDistributionViewSet,
)
from programs.views.ifashe_views.parent_views import (
    IfasheParentViewSet,
    ParentWorkContractViewSet,
    ParentAttendanceViewSet,
    ParentPerformanceViewSet,
)
from programs.views.ifashe_views.sponsorship_views import SponsorshipViewSet
from programs.views.ifashe_views.school_views import SchoolSupportViewSet
from programs.views.ifashe_views.all_reports_views import (
    FamilyOverviewPDFReportView,
    FamilyOverviewExcelReportView,
    IfasheSummaryPDFReportView,
    IfasheSummaryExcelReportView,
    IfasheSupportPDFReportView,
    IfasheSupportExcelReportView,
    ParentWorkPDFReportView,
    ParentWorkExcelReportView,
)

# Internships Views
from programs.views.internships_views.application_views import (
    InternshipApplicationViewSet,
)
