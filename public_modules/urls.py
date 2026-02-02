from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonorViewSet, DonationViewSet, CreatePaymentIntentView

router = DefaultRouter()
router.register(r'donors', DonorViewSet)
router.register(r'donations', DonationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-payment-intent/', CreatePaymentIntentView.as_view(), name='create-payment-intent'),
]
