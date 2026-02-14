from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ManagerViewset, LoginView, RequestPasswordResetView, ResetPasswordConfirmView, LogoutAPIView, ChangePasswordView, ActivityLogViewSet

router = DefaultRouter()
router.register('managers', ManagerViewset)
router.register('activity-logs', ActivityLogViewSet, basename='activity-logs')


urlpatterns = [
    path("managers/login/", LoginView.as_view()),
    path("managers/logout/", LogoutAPIView.as_view()),
    path("managers/password-reset/request/", RequestPasswordResetView.as_view()),
    path("managers/password-reset/confirm/", ResetPasswordConfirmView.as_view()),
    path("managers/change-password/", ChangePasswordView.as_view()),
]

urlpatterns += router.urls
