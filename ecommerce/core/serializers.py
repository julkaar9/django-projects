from rest_framework import serializers
from .models import AddedProduct, ShippingAddress, Order


class AddedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddedProduct
        fields = ("user", "product", "quantity", "status")


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = (
            "user",
            "name",
            "phone",
            "address_line1",
            "address_line2",
            "zip",
            "default_address",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "user",
            "price",
            "shipping_address",
        )
