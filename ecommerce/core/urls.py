from django.urls import path, re_path

from .views import (
    AddedProductView,
    CartView,
    CheckoutView,
    HomepageView,
    OrderView,
    ProductHomeView,
    ProductView,
    SearchView,
    ShippingAddressView,
)

app_name = "core"

urlpatterns = [
    path("", HomepageView.as_view(), name="home"),
    path("cart/", CartView.as_view(), name="cart"),
    path("history/", AddedProductView.as_view(), name="order_history"),
    path("products/", ProductHomeView.as_view(), name="product_home"),
    path("address/", ShippingAddressView.as_view(), name="address"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("order/", OrderView.as_view(), name="order"),
    path("search/", SearchView.as_view(), name="search"),
    re_path(r"cart/(?P<pk>\d+)/$", CartView.as_view(), name="cart_modify"),
    # re_path(
    #     r"added_product/(?P<pk>\d+)/$", AddedProductView.as_view(), name="added_product"
    # ),
    re_path(
        r"^products/(?P<slug>.+)/(?P<pk>\d+)/$", ProductView.as_view(), name="product"
    ),
]
