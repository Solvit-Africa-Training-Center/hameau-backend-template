from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ManagerViewset, LoginView, RequestPasswordResetView,ResetPasswordConfirmView

router = DefaultRouter()
router.register('managers',ManagerViewset)


urlpatterns = [
    path("managers/login/", LoginView.as_view()),
    path("managers/password-reset/request/", RequestPasswordResetView.as_view()),
    path("managers/password-reset/confirm/", ResetPasswordConfirmView.as_view()),
]

urlpatterns += router.urls
