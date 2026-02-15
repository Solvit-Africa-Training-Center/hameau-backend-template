from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GalleryCategoryViewSet, GalleryMediaViewSet

router = DefaultRouter()
router.register(r'gallery-categories', GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery-media', GalleryMediaViewSet, basename='gallery-media')

urlpatterns = [
    path('', include(router.urls)),
]

