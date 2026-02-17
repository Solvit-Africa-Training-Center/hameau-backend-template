from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonorViewSet, DonationViewSet, SponsorEmailLogViewSet

router = DefaultRouter()
router.register(r'donors', DonorViewSet, basename='donor')
router.register(r'donations', DonationViewSet, basename='donation')
router.register(r'email-logs', SponsorEmailLogViewSet, basename='donor-email-log')

urlpatterns = [
    path('', include(router.urls)),
]
