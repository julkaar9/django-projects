from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import AuthTokenObtainPairView, LoginAPIView, SignUpAPIView

app_name = "user"

urlpatterns = [
    path("token/", AuthTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("signup/", SignUpAPIView.as_view(), name="signup"),
]
