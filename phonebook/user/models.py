from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class AuthUser(AbstractUser):
    """The Authentication user model.

    Fields:
    -------
    username: required
    phone: required, unique, used for authentication
    email: optional, unique
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
    )
    phone = PhoneNumberField(
        _("phone"),
        unique=True,
        error_messages={
            "unique": _("A user with that phone number already exists."),
        },
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        validators=[validate_email],
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
        default=None,
        null=True,
        blank=True,
    )
    USERNAME_FIELD = "phone"
    # Password is inherited from AbstractUser and required by default
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.phone}({self.username})"
