from django.contrib.auth import authenticate, login
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuthUser


class LoginSerializers(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password", "placeholder": "Password"},
    )

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
            else:
                login(self.context.get("request"), user=user)
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        data["user"] = user
        return data


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password", "placeholder": "Password"},
    )

    class Meta:
        model = AuthUser
        fields = (
            "email",
            "phone",
            "password",
            "user_type",
            "first_name",
            "last_name",
        )

    def validate(self, data):
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")
        user_type = data.get("user_type")

        if self.partial:
            if len(data.keys()) == 0:
                msg = _("Empty attribute set")
                raise serializers.ValidationError(msg, code="authorization")

            elif password:
                msg = _("Password changing not allowed from this api")
                raise serializers.ValidationError(msg, code="authorization")

            elif email or user_type:
                msg = _("Cannot edit email and user_type")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            if email and phone and password and user_type:
                if AuthUser.objects.filter(
                    email=email,
                ).exists():
                    msg = _("email is not available")
                    raise serializers.ValidationError(msg, code="authorization")
            else:
                msg = _('Must include "email", "phone, "password" and "user_type".')
                raise serializers.ValidationError(msg, code="authorization")
        return data


class MyTokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.verified == False:
            raise serializers.ValidationError(
                _("Email Unverified"), code="authorization"
            )

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
