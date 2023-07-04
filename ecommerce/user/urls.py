from django.urls import path, re_path

from .views import LoginAPIView, LogoutView, SignUpView

app_name = "user"

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
]
