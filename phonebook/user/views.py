from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from user.serializers import (
    AuthTokenObtainPairSerializer,
    AuthUserSeriaizer,
    LoginSerializer,
)


class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, format=None):
        loginSerializer = LoginSerializer(
            context={"request": request}, data=request.data
        )
        if loginSerializer.is_valid(raise_exception=True):
            return Response(loginSerializer.data, status=status.HTTP_200_OK)
        else:
            return Response(loginSerializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class SignUpAPIView(GenericAPIView):
    serializer_class = AuthUserSeriaizer

    def post(self, request, format=None):
        signUpSerializer = AuthUserSeriaizer(
            context={"request": request}, data=request.data
        )
        if signUpSerializer.is_valid(raise_exception=True):
            signUpSerializer.save()
            return Response(signUpSerializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(signUpSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthTokenObtainPairView(TokenObtainPairView):
    serializer_class = AuthTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
