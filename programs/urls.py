from rest_framework.routers import DefaultRouter
from .views import (
    ChildViewSet,
    ChildProgressViewSet,
    EducationInstitutionViewSet,
    EducationProgramViewSet,
    ChildEducationViewSet,
    CaretakerViewSet,
    HealthRecordViewSet,
    ResidentialFinanceViewSet,
    IfasheFamilyViewSet,
    IfasheChildViewSet,
    IfasheParentViewSet,
)

router = DefaultRouter()

router.register('children', ChildViewSet, basename='child')
router.register('children_progress', ChildProgressViewSet, basename='progress')
router.register('children_educational_institutions', EducationInstitutionViewSet, basename='institution')
router.register('children_educational_programs', EducationProgramViewSet, basename='program')
router.register('children_programs_enrollments', ChildEducationViewSet, basename='enrollment')
router.register('caretakers', CaretakerViewSet, basename='caretaker')
router.register('health-records', HealthRecordViewSet, basename='health-record')
router.register('residential-finance', ResidentialFinanceViewSet, basename='residential-finance')
router.register('ifashe-families', IfasheFamilyViewSet, basename='ifashe-family')
router.register('ifashe-children', IfasheChildViewSet, basename='ifashe-child')
router.register('ifashe-parents', IfasheParentViewSet, basename='ifashe-parent')

urlpatterns = router.urls

