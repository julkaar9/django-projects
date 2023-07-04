from django.contrib.auth import authenticate, login
from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    PasswordField,
    TokenObtainPairSerializer,
)

from .models import AuthUser


class LoginSerializer(serializers.Serializer):
    phone = PhoneNumberField()
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Leave empty if no change needed",
        style={"input_type": "password", "placeholder": "Password"},
    )

    def validate(self, data):
        phone = str(data.get("phone"))
        password = data.get("password")
        if phone and password:
            user = authenticate(
                request=self.context.get("request"),
                username=phone,
                password=password,
            )
            print(user)
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")
            else:
                login(self.context.get("request"), user=user)
        else:
            msg = _('Must include "phone" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        data["user"] = user
        return data


class AuthUserSeriaizer(serializers.ModelSerializer):
    phone = PhoneNumberField()
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Leave empty if no change needed",
        style={"input_type": "password", "placeholder": "Password"},
    )
    email = serializers.EmailField(required=False)

    class Meta:
        model = AuthUser
        fields = ("phone", "password", "username", "email")

    def validate(self, data):
        phone = str(data.get("phone"))
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        if self.partial:
            if len(data.keys()) == 0:
                msg = _("Empty attribute set")
                raise serializers.ValidationError(msg, code="authorization")

            elif password:
                msg = _("Password changing not allowed currently")
                raise serializers.ValidationError(msg, code="authorization")

            elif phone:
                msg = _("Cannot edit phone number currently")
                raise serializers.ValidationError(msg, code="authorization")
        else:
            if phone and password and username:
                if email:
                    if AuthUser.objects.filter(email=email).exists():
                        msg = _("Email is already registered")
                        raise serializers.ValidationError(msg, code="authorization")
                if AuthUser.objects.filter(phone=phone).exists():
                    msg = _("Phone number is already registered")
                    raise serializers.ValidationError(msg, code="authorization")
            else:
                msg = _("Must include phone number, name,  password.")
                raise serializers.ValidationError(msg, code="authorization")
        return data

    def create(self, validated_data):
        # Monkey patching as unique and nullable email
        # field throws IntegrityError
        email = validated_data.get("email", None)
        if email is None:
            validated_data["email"] = (
                "".join((c for c in str(validated_data["phone"]) if c.isdigit()))
                + "@mail.com"
            )

        user = AuthUser.objects.create_user(**validated_data)

        if email is None:
            user.email = None
            user.save()
        return user


class AuthTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = PhoneNumberField()
        self.fields["password"] = PasswordField()

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["phone"] = str(user.phone)
        return token
