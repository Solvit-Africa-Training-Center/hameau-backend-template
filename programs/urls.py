from rest_framework.routers import DefaultRouter
from .views import (
    ChildViewSet,
    ChildProgressViewSet,
    EducationInstitutionViewSet,
    EducationProgramViewSet,
    ChildEducationViewSet,
    CaretakerViewSet,
    HealthRecordViewSet,
<<<<<<< Updated upstream
=======
    ResidentialFinanceViewSet,
    IfasheFamilyViewSet,
    IfasheChildViewSet,
    IfasheParentViewSet,
    SponsorshipViewSet,
    SchoolSupportViewSet,
    DressingDistributionViewSet,
    ParentWorkContractViewSet,
    ParentAttendanceViewSet,
    ParentPerformanceViewSet,
>>>>>>> Stashed changes
)

router = DefaultRouter()

router.register('children', ChildViewSet, basename='child')
router.register('children_progress', ChildProgressViewSet, basename='progress')
router.register('children_educational_institutions', EducationInstitutionViewSet, basename='institution')
router.register('children_educational_programs', EducationProgramViewSet, basename='program')
router.register('children_programs_enrollments', ChildEducationViewSet, basename='enrollment')
router.register('caretakers', CaretakerViewSet, basename='caretaker')
router.register('health-records', HealthRecordViewSet, basename='health-record')
<<<<<<< Updated upstream
=======
router.register('residential-finance', ResidentialFinanceViewSet, basename='residential-finance')
router.register('ifashe-families', IfasheFamilyViewSet, basename='ifashe-family')
router.register('ifashe-children', IfasheChildViewSet, basename='ifashe-child')
router.register('ifashe-parents', IfasheParentViewSet, basename='ifashe-parent')
router.register('ifashe-sponsorships', SponsorshipViewSet, basename='ifashe-sponsorship')
router.register('ifashe-school-support', SchoolSupportViewSet, basename='ifashe-school-support')
router.register('ifashe-dressing-distributions', DressingDistributionViewSet, basename='ifashe-dressing-distribution')
router.register('ifashe-parent-work-contracts', ParentWorkContractViewSet, basename='ifashe-parent-work-contract')
router.register('ifashe-parent-attendance', ParentAttendanceViewSet, basename='ifashe-parent-attendance')
router.register('ifashe-parent-performance', ParentPerformanceViewSet, basename='ifashe-parent-performance')
>>>>>>> Stashed changes

urlpatterns = router.urls

