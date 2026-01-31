from rest_framework.routers import DefaultRouter
from .views import (
    ChildViewSet,
    ChildProgressViewSet,
    EducationInstitutionViewSet,
    EducationProgramViewSet,
    ChildEducationViewSet,
)

router = DefaultRouter()

router.register('children', ChildViewSet, basename='child')
router.register('children_progress', ChildProgressViewSet, basename='progress')
router.register('children_educational_institutions', EducationInstitutionViewSet, basename='institution')
router.register('children_educational_programs', EducationProgramViewSet, basename='program')
router.register('children_programs_enrollments', ChildEducationViewSet, basename='enrollment')

urlpatterns = router.urls

