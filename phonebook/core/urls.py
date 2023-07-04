from django.urls import path

from .views import (
    ContactView,
    SearchView,
    PhoneDetailsView,
    SpamView,
)

app_name = "core"

urlpatterns = [
    path("contacts/", ContactView.as_view(), name="contacts"),
    path("spam/", SpamView.as_view(), name="spam"),
    path("search/", SearchView.as_view(), name="search"),
    path("phone-directory/", PhoneDetailsView.as_view(), name="phone_directory"),
]
