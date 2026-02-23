from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.gallery_views import GalleryCategoryViewSet, GalleryMediaViewSet
from .views.impact_views import ImpactStatsView
from .views.team_views import TeamMemberViewSet

router = DefaultRouter()
router.register(r'gallery-categories', GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery-media', GalleryMediaViewSet, basename='gallery-media')
router.register(r'team-members', TeamMemberViewSet, basename='team-member')

urlpatterns = [
    path('impact/', ImpactStatsView.as_view(), name='impact-stats'),
    path('', include(router.urls)),
]

