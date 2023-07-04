from django.db.models import Q
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AddedProduct, Product, ShippingAddress
from .serializers import AddedProductSerializer, AddressSerializer, OrderSerializer


class HomepageView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "core/home.html"

    def get(self, request):
        new_products = Product.objects.filter(label="NEW", TNA=False, stock__gt=0)
        categories = Product.objects.values(
            "category__name", "category__description", "category__image"
        ).distinct()
        return Response({"new_products": new_products, "categories": categories})


class ProductView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "core/product.html"

    def _get_product(self, pk):
        product = Product.objects.get(pk=pk, TNA=False, stock__gt=0)
        added_product = AddedProduct.objects.filter(
            product=product, status="WISH_LIST"
        ).last()
        return product, added_product

    def get(self, request, slug, pk):
        product, added_product = self._get_product(pk)
        if not added_product:
            addedProductSerializer = AddedProductSerializer()
        else:
            addedProductSerializer = AddedProductSerializer(added_product)
        return Response({"product": product, "serializer": addedProductSerializer})

    def post(self, request, slug, pk):
        product, added_product = self._get_product(pk)
        data = {
            "user": request.user.pk,
            "product": product.pk,
            "quantity": int(request.data.get("quantity")),
            "status": "WISH_LIST",
        }

        addedProductSerializer = AddedProductSerializer(added_product, data=data)

        if addedProductSerializer.is_valid(raise_exception=False):
            addedProductSerializer.save()
            return Response({"product": product, "serializer": addedProductSerializer})
        else:
            return Response(
                {"product": product, "errors": addedProductSerializer.errors}
            )


class ProductHomeView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "core/product_home.html"

    def get(self, request):
        categories = request.GET.getlist("categories", None)
        label = request.GET.get("label")

        q_filter = ~Q(pk__in=[])
        if categories:
            q_filter &= Q(category__name__in=categories)
        if label:
            q_filter &= Q(label=label)

        products = Product.objects.filter(q_filter)
        categories = Product.objects.values("category__name").distinct()
        labels = ["DEFAULT", "NEW", "SALE", "BEST_SELLER"]
        return Response(
            {"products": products, "categories": categories, "product_labels": labels}
        )


class CartView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "core/cart.html"

    permission_classes = [IsAuthenticated]

    def get(self, request):
        added_products = AddedProduct.objects.filter(
            user=request.user.pk, status="WISH_LIST", quantity__gt=0
        )
        total_price = 0
        for added_product in added_products:
            total_price += added_product.get_total_item_price()

        return Response({"added_products": added_products, "total_price": total_price})

    def post(self, request, pk):
        action = request.data.get("quantity")

        added_product = AddedProduct.objects.filter(pk=pk, status="WISH_LIST").last()
        if action == "decrease":
            added_product.quantity -= 1
            if added_product.quantity == 0:
                added_product.delete()
            else:
                added_product.save()
        elif action == "increase":
            added_product.quantity += 1
            added_product.save()
        elif action == "remove":
            added_product.quantity = 0
            added_product.delete()
        return redirect("core:cart")


class AddedProductView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "core/orders.html"
    permission_classes = [IsAuthenticated]

    def get(self, request):
        added_products = AddedProduct.objects.filter(
            user=request.user.pk, status__in=["ORDERED", "SHIPPED"], quantity__gt=0
        )

        return Response({"added_products": added_products})


class ShippingAddressView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    permission_classes = [IsAuthenticated]
    template_name = "core/address.html"
    response_content = {"title": "Login", "errors": []}

    def _disable_old_default_addr(self):
        addr = ShippingAddress.objects.filter(default_address=True).last()
        if addr:
            addr.default_address = False
            addr.save()

    def get(self, request):
        address = ShippingAddress.objects.filter(user=request.user.pk).last()
        self.response_content["serializer"] = AddressSerializer(address)
        return Response(self.response_content)

    def post(self, request):
        data = request.data.copy()
        data["user"] = request.user.pk
        data["default_address"] = (
            True if data.get("default_address", "off") == "on" else False
        )
        if data["default_address"]:
            self._disable_old_default_addr()

        addresSerializer = AddressSerializer(data=data)
        if addresSerializer.is_valid(raise_exception=True):
            self.response_content["serializer"] = addresSerializer
            addresSerializer.save()
        else:
            self.response_content["errors"] = addresSerializer.errors
        return Response(self.response_content)


class CheckoutView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    permission_classes = [IsAuthenticated]
    template_name = "core/checkout.html"
    response_content = {"title": "checkout", "errors": []}

    def get(self, request):
        address = request.GET.get("address")
        added_products = AddedProduct.objects.filter(
            user=request.user.pk, status="WISH_LIST", quantity__gt=0
        )

        shipping_addresses = ShippingAddress.objects.filter(
            user=request.user.pk
        ).values("pk", "name", "phone")
        if not address:
            chosen_address = ShippingAddress.objects.filter(
                user=request.user.pk, default_address=True
            ).last()
        else:
            chosen_address = ShippingAddress.objects.filter(
                user=request.user.pk, pk=address
            ).last()
        return Response(
            {
                "added_products": added_products,
                "shipping_addresses": shipping_addresses,
                "chosen_address": chosen_address,
            }
        )


class OrderView(APIView):
    permission_classes = [IsAuthenticated]
    response_content = {"title": "Order", "errors": []}

    def post(self, request):
        address = request.data.get("selected_address")
        if address:
            added_products = AddedProduct.objects.filter(
                user=request.user.pk, status="WISH_LIST", quantity__gt=0
            )
            total_price = 0
            for added_product in added_products:
                total_price += added_product.get_total_item_price()

            orderSerialzer = OrderSerializer(
                data={
                    "user": request.user.pk,
                    "price": total_price,
                    "shipping_address": address,
                }
            )
            if orderSerialzer.is_valid():
                order = orderSerialzer.save()
                added_products.update(status="ORDERED", order=order)
                return redirect("core:cart")

        return redirect("core:checkout")


class SearchView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "core/search.html"

    def get(self, request):
        product = Product.objects.filter(title__icontains="asus")
        return Response()

    def post(self, request):
        keyword = request.data.get("search")
        if keyword:
            products = Product.objects.filter(title__icontains=keyword)
            return Response({"products": products})
        else:
            return redirect("core:home")
