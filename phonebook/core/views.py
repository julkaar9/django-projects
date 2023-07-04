from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from user.models import AuthUser

from .models import Contact, PhoneDirectory, SpamData
from .serializers import (
    ContactSerializer,
    PhoneSearchSerializer,
    SpamDataSerializer,
)


class HomeView(APIView):
    def get(self, request, format=None):
        url_routes = {
            "swagger docs": reverse(
                "schema-swagger-ui", request=request, format=format
            ),
        }
        return Response(url_routes)


class BaseUserXPhoneDirectoryView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    model = None
    serializer_class = None
    user_field = None

    def get(self, request):
        if request.user.is_staff:
            query_set = self.model.objects.all()
        else:
            query_set = self.model.objects.filter(**{self.user_field: request.user})

        query_json = self.serializer_class(query_set, many=True).data
        return Response(query_json, status=status.HTTP_200_OK)

    def post(self, request):
        request.data[self.user_field] = request.user.id
        serializer = self.serializer_class(
            context={"request": request}, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactView(BaseUserXPhoneDirectoryView):
    model = Contact
    serializer_class = ContactSerializer
    user_field = "user"


class SpamView(BaseUserXPhoneDirectoryView):
    model = SpamData
    serializer_class = SpamDataSerializer
    user_field = "reporter_phone"


class PhoneDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "q",
                openapi.IN_QUERY,
                description="phone number",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def get(self, request):
        user = request.user
        phone_query = request.query_params.get("q")
        phone_number = PhoneNumber.from_string(phone_query)
        if not phone_query or not phone_number.is_valid():
            return Response(
                {"error": "Invalid Phone number"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            phone_instance = PhoneDirectory.objects.get(phone=phone_number)
            hide_email = True
            if Contact.objects.filter(user=user, phone__phone=phone_number).exists():
                hide_email = False
            phone_json = PhoneSearchSerializer(
                phone_instance, hide_email=hide_email
            ).data
            return Response(phone_json, status=status.HTTP_200_OK)


class SearchView(APIView):
    permission_classes = [IsAuthenticated]

    class BaseNameSerializer(serializers.Serializer):
        type = serializers.SerializerMethodField()
        name = serializers.SerializerMethodField()
        spam_count = serializers.SerializerMethodField()

        def get_type(self, obj):
            raise NotImplementedError

        def get_name(self, obj):
            raise NotImplementedError

        def get_spam_count(self, obj):
            raise NotImplementedError

    class RegisteredNameSerializer(BaseNameSerializer):
        phone = PhoneNumberField()

        def get_type(self, obj):
            return "registered"

        def get_name(self, obj):
            return obj.username

        def get_spam_count(self, obj):
            return obj.phone_dir.spam_reports.count()

        def to_representation(self, instance):
            data = super().to_representation(instance)
            data.update({"phone": str(instance.phone_dir.phone)})
            return data

    class ContactNameSerializer(BaseNameSerializer):
        phone = PhoneNumberField()

        def get_type(self, obj):
            return "unregistered"

        def get_name(self, obj):
            return obj.name

        def get_spam_count(self, obj):
            return obj.phone.spam_reports.count()

        def to_representation(self, instance):
            data = super().to_representation(instance)
            data.update({"phone": str(instance.phone.phone)})
            return data

    class SpamNameSerializer(BaseNameSerializer):
        target_phone = PhoneNumberField()

        def get_type(self, obj):
            return "reported spam"

        def get_name(self, obj):
            return obj.name

        def get_spam_count(self, obj):
            return obj.target_phone.spam_reports.count()

        def to_representation(self, instance):
            data = super().to_representation(instance)
            data.pop("target_phone")
            data.update({"phone": str(instance.target_phone.phone)})
            return data

    def name_search(self, name_query):
        prefix_queries = []
        substring_queries = []
        if name_query != None:
            for model, name_field, serializer in zip(
                [AuthUser, Contact, SpamData],
                ["username", "name", "name"],
                [
                    self.RegisteredNameSerializer,
                    self.ContactNameSerializer,
                    self.SpamNameSerializer,
                ],
            ):
                prefix_matches = model.objects.filter(
                    **{f"{name_field}__startswith": name_query}
                )
                substring_matches = model.objects.filter(
                    **{f"{name_field}__iregex": r".+" + name_query}
                )
                prefix_data = serializer(prefix_matches, many=True).data
                substring_data = serializer(substring_matches, many=True).data
                prefix_queries.extend(prefix_data)
                substring_queries.extend(substring_data)
            return Response(
                prefix_queries + substring_queries,
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"Invalid Name"}, status=status.HTTP_400_BAD_REQUEST)

    def phone_search(self, phone_query):
        phone_number = PhoneNumber.from_string(phone_query)
        if phone_number.is_valid():
            try:
                phone_instance = PhoneDirectory.objects.get(phone=phone_number)
            except ObjectDoesNotExist:
                return Response(
                    {"error": "Invalid Phone number"}, status=status.HTTP_404_NOT_FOUND
                )

            query_json = []
            if phone_instance.user:
                query_json = [self.RegisteredNameSerializer(phone_instance.user).data]
            else:
                from_contacts = phone_instance.aliases.all()
                from_spam = phone_instance.spam_reports.all()
                for data, serializer in zip(
                    [from_contacts, from_spam],
                    [
                        self.ContactNameSerializer,
                        self.SpamNameSerializer,
                    ],
                ):
                    query_json.extend(serializer(data, many=True).data)
            return Response(query_json, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid Phone number"}, status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "name",
                openapi.IN_QUERY,
                description="search by name",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "phone",
                openapi.IN_QUERY,
                description="search by phone",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def get(self, request):
        name_query = request.query_params.get("name")

        phone_query = request.query_params.get("phone")
        if name_query and phone_query:
            return Response(
                {"message": "Both name and phone search not allowed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if name_query:
            return self.name_search(name_query)
        elif phone_query:
            return self.phone_search(phone_query)
        else:
            return Response(
                {"message": "No search query provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
