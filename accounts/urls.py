from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ManagerViewset, LoginView, LogoutAPIView

router = DefaultRouter()
router.register('managers',ManagerViewset)


urlpatterns = [
    path("managers/login/", LoginView.as_view()),
    path("managers/logout/", LogoutAPIView.as_view())
]

urlpatterns += router.urls
