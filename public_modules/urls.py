from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.gallery_views import GalleryCategoryViewSet, GalleryMediaViewSet
from .views.impact_views import (
    ContactMessageViewSet,
    ContactMessageCreateView,
    ImpactStatisticListView,
    ImpactStatisticViewSet,
    ContactInfoListView,
    ContactInfoViewSet,
)
from .views.team_views import TeamMemberListView, TeamMemberViewSet

router = DefaultRouter()
router.register(r'gallery-categories', GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery-media', GalleryMediaViewSet, basename='gallery-media')
router.register(r'contact-messages', ContactMessageViewSet, basename='contact-messages')
router.register(r'impact-statistics', ImpactStatisticViewSet, basename='impact-statistics')
router.register(r'contact-info', ContactInfoViewSet, basename='contact-info')
router.register(r'team-members', TeamMemberViewSet, basename='team-members')

urlpatterns = [
    # Public endpoints
    path('contact-messages/create/', ContactMessageCreateView.as_view(), name='contact-create'),
    path('impact-statistics/public/', ImpactStatisticListView.as_view(), name='impact-statistics-list'),
    path('contact-info/public/', ContactInfoListView.as_view(), name='contact-info-list'),
    path('team-members/public/', TeamMemberListView.as_view(), name='team-members-list'),
    # All viewsets
    path('', include(router.urls)),
]
