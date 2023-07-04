from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
from user.models import AuthUser

# Create your models here.
class PhoneDirectory(models.Model):
    """Global Phone Directory.
    This model instances never should be deleted by normal means.

    Fields
    -------
    phone: primary key, required, unique
    user: One to One relation to authuser, optional
    """

    phone = PhoneNumberField(
        _("phone"),
        primary_key=True,
        error_messages={
            "unique": _("Phone number already exists in directory"),
        },
    )
    user = models.OneToOneField(
        AuthUser,
        related_name="phone_dir",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self) -> str:
        return "".join(
            (str(self.phone), f"({self.user.username})*" if self.user else "")
        )

    class Meta:
        verbose_name = "Phone instance"
        verbose_name_plural = "Phone directory"


class Contact(models.Model):
    """user contact numbers model.

    Fields
    -------
    user: Contacts are imported from this user, required
    phone: These phone numbers are imported, required
    name: Contact name given by user, optional
    """

    user = models.ForeignKey(
        AuthUser,
        null=True,
        related_name="contacts",
        related_query_name="contact",
        on_delete=models.SET_NULL,
    )
    phone = models.ForeignKey(
        PhoneDirectory, related_name="aliases", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = "contact"
        verbose_name_plural = "contacts"
        constraints = [
            UniqueConstraint(
                fields=["user", "phone", "name"], name="unique_with_optional"
            ),
            UniqueConstraint(
                fields=["user", "phone"],
                condition=Q(name=None),
                name="unique_without_optional",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user.phone} -> {self.phone}({self.name})"


class SpamData(models.Model):
    """Model for Spam data.

    Fields
    -------
    target_phone: Phone directory instance of potential spammer, required
    reporter_phone: Authuser instance of the user that reported, required
    name: Potential spammer name, optional
    """

    target_phone = models.ForeignKey(
        PhoneDirectory,
        related_name="spam_reports",
        on_delete=models.CASCADE,
    )
    reporter_phone = models.ForeignKey(
        AuthUser, related_name="spams_reported", on_delete=models.SET_NULL, null=True
    )
    name = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        verbose_name = "spam"
        verbose_name_plural = "spam items"
        constraints = [
            UniqueConstraint(
                fields=["target_phone", "reporter_phone", "name"],
                name="spam_unique_with_optional",
            ),
            UniqueConstraint(
                fields=["target_phone", "reporter_phone"],
                condition=Q(name=None),
                name="spam_unique_without_optional",
            ),
        ]

    def __str__(self) -> str:
        return f"spam:{self.target_phone}({self.name})"


@receiver(post_save, sender=AuthUser)
def create_phone_directory(sender, instance, created, **kwargs):
    """Polpulates the phone directory's one to one user
    on every new user registration"""
    if created:
        phone_instance, _ = PhoneDirectory.objects.get_or_create(phone=instance.phone)
        phone_instance.user = instance
        phone_instance.save()
