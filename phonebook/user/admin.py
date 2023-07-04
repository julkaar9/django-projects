from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import AuthUser


class AuthUserAdminView(UserAdmin):
    model = AuthUser
    fieldsets = (
        ("Info", {"fields": ("username", "phone", "password", "email")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "phone", "email", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ["last_login"]
    list_display = ("username", "phone", "email", "is_staff")

    def name(self, obj):
        return obj.first_name + " " + obj.last_name


admin.site.register(AuthUser, AuthUserAdminView)
