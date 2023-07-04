from django.contrib import admin

from .models import Contact, PhoneDirectory, SpamData

# Register your models here.


class ContactAdminView(admin.ModelAdmin):
    model = Contact
    fieldsets = (("Info", {"fields": ("user", "phone", "name")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user", "phone", "name"),
            },
        ),
    )
    list_display = ("user", "phone", "name")


class PhoneDirectoryAdminView(admin.ModelAdmin):
    model = PhoneDirectory
    fieldsets = (("Info", {"fields": ("user", "phone")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("user", "phone"),
            },
        ),
    )
    list_display = ("user", "phone", "spam_reports", "aliases")

    def spam_reports(self, obj):
        return obj.spam_reports.count()

    def aliases(self, obj):
        return ", ".join([str(alias.name) for alias in obj.aliases.all()])


class SpamDataAdminView(admin.ModelAdmin):
    model = SpamData
    fieldsets = (("Info", {"fields": ("target_phone", "reporter_phone", "name")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("target_phone", "reporter_phone", "name"),
            },
        ),
    )
    list_display = ("target_phone", "reporter_phone", "name")


admin.site.register(PhoneDirectory, PhoneDirectoryAdminView)
admin.site.register(Contact, ContactAdminView)
admin.site.register(SpamData, SpamDataAdminView)
