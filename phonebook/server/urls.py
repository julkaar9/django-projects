"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from core.views import HomeView

schema_view = get_schema_view(
    openapi.Info(
        title="Phonebook API",
        default_version="v1",
        description="Endpoints for phonebook",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="julkaar9@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    authentication_classes=(SessionAuthentication, BasicAuthentication),
    permission_classes=[permissions.AllowAny],
)

yasg_urlpatterns = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("api/", include("core.urls", namespace="core")),
    path("admin/", admin.site.urls),
    path("user/", include("user.urls", namespace="user")),
]

urlpatterns += yasg_urlpatterns
