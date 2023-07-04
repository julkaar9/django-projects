from django.contrib.auth import login, logout
from django.shortcuts import redirect
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializers, SignUpSerializer

# Create your views here.


class LoginAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "user/login.html"
    response_content = {"title": "Login", "errors": []}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, format=None):
        self.response_content["serializer"] = LoginSerializers()

        return Response(self.response_content)

    def post(self, request, format=None):
        loginSerializer = LoginSerializers(
            context={"request": request}, data=request.data
        )
        if loginSerializer.is_valid(raise_exception=False):
            self.response_content["serializer"] = loginSerializer
            return redirect("core:home")
        else:
            self.response_content["errors"] = loginSerializer.errors
        return Response(self.response_content)


class LogoutView(APIView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("user:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        logout(request)
        return redirect("user:login")


class SignUpView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "user/signup.html"
    response_content = {"title": "Login", "errors": []}

    def get(self, request, format=None):
        self.response_content["serializer"] = SignUpSerializer()

        return Response(self.response_content)

    def post(self, request, format=None):
        signUpSerializer = SignUpSerializer(
            context={"request": request}, data=request.data
        ) 
        if signUpSerializer.is_valid(raise_exception=False):
            self.response_content["serializer"] = signUpSerializer
            user = signUpSerializer.save()
            login(request, user=user)
            return redirect("core:home")
        else:
            self.response_content["errors"] = signUpSerializer.errors
        return Response(self.response_content)
