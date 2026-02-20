from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.gallery_views import GalleryCategoryViewSet, GalleryMediaViewSet
from .views.content_views import (
    PublicContentViewSet,
    ContactMessageViewSet,
    TeamMemberViewSet,
    SuccessStoryViewSet
)

router = DefaultRouter()
router.register(r'gallery-categories', GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery-media', GalleryMediaViewSet, basename='gallery-media')
router.register(r'content', PublicContentViewSet, basename='public-content')
router.register(r'contact-messages', ContactMessageViewSet, basename='contact-messages')
router.register(r'team', TeamMemberViewSet, basename='team-members')
router.register(r'success-stories', SuccessStoryViewSet, basename='success-stories')

urlpatterns = [
    path('', include(router.urls)),
]
