from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

def homeDocs(request):
    return render(request, "home1.html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls")),
    path("api/", include("programs.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("swagger.json", SpectacularAPIView.as_view(), name="schema-json"),
    path(
        "rapidoc/", TemplateView.as_view(template_name="rapidoc.html"), name="rapidoc"
    ),
    path("", homeDocs, name="home"),
    path("api/", include("public_modules.urls")),
    path("api/donations/", include("donations.urls")),
]
