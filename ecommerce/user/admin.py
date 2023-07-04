from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import AuthUser


class AuthUserAdminView(UserAdmin):
    model = AuthUser
    fieldsets = (
        (None, {"fields": ("email", "email_verified", "user_type")}),
        (
            _("Personal info"),
            {"fields": ("phone", "phone_verified", "first_name", "last_name")},
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user_type", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ["last_login"]
    list_display = (
        "email",
        "email_verified",
        "phone",
        "phone_verified",
        "user_type",
        "name",
        "is_staff",
    )
    search_fields = ("email", "phone", "first_name", "last_name")
    ordering = ("email",)

    def name(self, obj):
        return obj.first_name + " " + obj.last_name


admin.site.register(AuthUser, AuthUserAdminView)
