<<<<<<< HEAD
from programs.views.residentials_views.child_views import *
from programs.views.residentials_views.caretaker_views import *
from programs.views.residentials_views.health_record_views import *
from programs.views.residentials_views.residential_finance_views import *
from programs.views.ifashe_views.family_views import *
from programs.views.ifashe_views.child_views import *
from programs.views.ifashe_views.parent_views import *
from programs.views.ifashe_views.sponsorship_views import *
from programs.views.ifashe_views.school_views import *
from programs.views.internships_views import *
=======
# Residentials Views
from .residentials_views.child_views import (
    ChildViewSet,
    ChildProgressViewSet,
    EducationInstitutionViewSet,
    EducationProgramViewSet,
    ChildEducationViewSet,
)
from .residentials_views.caretaker_views import CaretakerViewSet
from .residentials_views.health_record_views import HealthRecordViewSet
from .residentials_views.residential_finance_views import (
    ResidentialFinanceViewSet,
    ResidentialFinanceExcelReportView,
    ResidentialFinancePDFReportView,
)

# Ifashe Views
from .ifashe_views.family_views import IfasheFamilyViewSet
from .ifashe_views.child_views import (
    IfasheChildViewSet, 
    DressingDistributionViewSet
)
from .ifashe_views.parent_views import (
    IfasheParentViewSet,
    ParentWorkContractViewSet,
    ParentAttendanceViewSet,
    ParentPerformanceViewSet,
)
from .ifashe_views.sponsorship_views import SponsorshipViewSet
from .ifashe_views.school_views import SchoolSupportViewSet
from .ifashe_views.all_reports_views import (
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
from .internships_views.application_views import InternshipApplicationViewSet
>>>>>>> e5007aa329cde90bb4138dd96c1d4ef871f9a328
