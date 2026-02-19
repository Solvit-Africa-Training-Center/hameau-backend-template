from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.gallery_views import GalleryCategoryViewSet, GalleryMediaViewSet
from .views.content_views import ContactMessageViewSet, TeamViewSet, StoryViewSet, ImpactViewSet

router = DefaultRouter()
router.register(r'gallery-categories', GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery-media', GalleryMediaViewSet, basename='gallery-media')
# Specific Public Content Routes
router.register(r'team', TeamViewSet, basename='team')
router.register(r'stories', StoryViewSet, basename='stories')
router.register(r'impact-stats', ImpactViewSet, basename='impact-stats')
# Contact Messages
router.register(r'contact-messages', ContactMessageViewSet, basename='contact-message')

urlpatterns = [
    # All viewsets
    path('', include(router.urls)),
]
