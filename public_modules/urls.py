from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.gallery_views import GalleryCategoryViewSet, GalleryMediaViewSet
from .views.content_views import ImpactViewSet, TeamViewSet, StoryViewSet, ContactMessageViewSet

router = DefaultRouter()
router.register(r'gallery-categories', GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery-media', GalleryMediaViewSet, basename='gallery-media')
router.register(r'impact-stats', ImpactViewSet, basename='impact-stats')
router.register(r'team', TeamViewSet, basename='team')
router.register(r'success-stories', StoryViewSet, basename='success-stories')
router.register(r'contact-messages', ContactMessageViewSet, basename='contact-messages')

urlpatterns = [
    # All viewsets
    path('', include(router.urls)),
]
