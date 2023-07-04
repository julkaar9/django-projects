from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _gl
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from user.serializers import AuthUserSeriaizer

from .models import Contact, PhoneDirectory, SpamData


class PhoneDirectorySerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()

    class Meta:
        model = PhoneDirectory
        fields = ("user", "phone")


class PhoneSearchSerializer(serializers.Serializer):
    def getAliasSerializer(self, model_arg):
        class AliasSerializer(serializers.ModelSerializer):
            class Meta:
                model = model_arg
                fields = ("name",)

        return AliasSerializer

    user = serializers.SerializerMethodField()
    phone = PhoneNumberField()
    spam_count = serializers.SerializerMethodField()
    contact_count = serializers.SerializerMethodField()
    spam_aliases = serializers.SerializerMethodField()
    contact_aliases = serializers.SerializerMethodField()

    def __init__(self, *args, hide_email=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.hide_email = hide_email

    def get_user(self, obj):
        json = AuthUserSeriaizer(obj.user).data
        if self.hide_email:
            json["email"] = None
        return json

    def remove_nulls(self, result_list):
        return [result for result in result_list if result.get("name") is not None]

    def get_spam_count(self, obj):
        return obj.spam_reports.count()

    def get_contact_count(self, obj):
        return obj.aliases.count()

    def get_spam_aliases(self, obj):
        serializer = self.getAliasSerializer(SpamData)
        result_list = serializer(obj.spam_reports, many=True).data
        return self.remove_nulls(result_list)

    def get_contact_aliases(self, obj):
        serializer = self.getAliasSerializer(Contact)
        result_list = serializer(obj.aliases, many=True).data
        return self.remove_nulls(result_list)


class SpamDataSerializer(serializers.ModelSerializer):
    target_phone = PhoneNumberField()

    class Meta:
        model = SpamData
        fields = ("target_phone", "reporter_phone", "name")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update({"target_phone": str(instance.target_phone.phone)})
        return data

    def create(self, validated_data):
        target_phone = validated_data.pop("target_phone")
        phone_instance, _ = PhoneDirectory.objects.get_or_create(phone=target_phone)

        try:
            instance = SpamData.objects.create(
                target_phone=phone_instance, **validated_data
            )
        except IntegrityError:
            msg = _gl("Already reported this number")
            raise serializers.ValidationError(msg)
        return instance


class ContactSerializer(serializers.ModelSerializer):
    phone = PhoneNumberField()

    class Meta:
        model = Contact
        fields = ("user", "phone", "name")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Unfortunate naming, was too late to change
        data.update({"phone": str(instance.phone.phone)})
        return data

    def create(self, validated_data):
        phone_data = validated_data.pop("phone")
        phone_instance, _ = PhoneDirectory.objects.get_or_create(phone=phone_data)
        try:
            instance = Contact.objects.create(phone=phone_instance, **validated_data)
        except IntegrityError:
            msg = _gl("Contact is previously added")
            raise serializers.ValidationError(msg)
        return instance
