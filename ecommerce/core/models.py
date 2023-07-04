import uuid

from django.db import models
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from user.models import AuthUser

# Create your models here.


def category_image_path(instance, filename):
    filename = f"{instance.name}.{filename.split('.')[-1]}"
    return f"category_image_path/{filename}"


def product_image_path(instance, filename):
    filename = f"{instance.title}.{filename.split('.')[-1]}"
    return f"product_image_path/{filename}"


def carousel_image_path(instance, filename):
    filename = f"{instance.name}.{filename.split('.')[-1]}"
    return f"carousel_image_path/{filename}"


class Carousel(models.Model):
    title = models.CharField(max_length=128)
    text = models.CharField(max_length=128)
    link = models.CharField(max_length=128)
    image = models.ImageField(upload_to=carousel_image_path)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(unique=True, max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(upload_to=category_image_path, null=True, blank=True)
    sub_category = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="parent_categories",
        related_query_name="parent_category",
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    @classmethod
    def get_default_pk(cls):
        others, _ = cls.objects.get_or_create(
            name="Others", defaults=dict(description="Other categories")
        )
        return others.pk

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    LABEL_CHOICES = (
        ("DEFAULT", "Default"),
        ("NEW", "New"),
        ("SALE", "Sale"),
        ("BEST_SELLER", "Best Seller"),
    )
    created_at = models.DateTimeField("date added", auto_now_add=True)
    updated_at = models.DateTimeField("last updated", auto_now=True)

    title = models.CharField(max_length=128)
    slug = models.SlugField()
    description = models.CharField(max_length=128)
    label = models.CharField(choices=LABEL_CHOICES, max_length=32, default="NEW")
    image = models.ImageField(upload_to=product_image_path, null=True, blank=True)

    price = models.PositiveIntegerField()
    discount_price = models.PositiveIntegerField(blank=True, null=True)
    stock = models.PositiveIntegerField()
    TNA = models.BooleanField(default=False)

    category = models.ForeignKey(
        Category,
        related_name="products",
        related_query_name="product",
        default=Category.get_default_pk,
        on_delete=models.CASCADE,
    )

    def cost(self):
        return self.price / 100

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ShippingAddress(models.Model):
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    phone = PhoneNumberField(region="IN")
    address_line1 = models.CharField(max_length=128)
    address_line2 = models.CharField(max_length=128, null=True, blank=True)
    zip = models.CharField(max_length=100)
    default_address = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        verbose_name_plural = "ShippingAddresses"


class Order(models.Model):
    number = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField("date created", auto_now_add=True)
    updated_at = models.DateTimeField("last updated", auto_now=True)

    price = models.PositiveBigIntegerField()
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True
    )


class AddedProduct(models.Model):
    STATUS = (
        ("WISH_LIST", "Wish List"),
        ("ORDERED", "Ordered"),
        ("SHIPPED", "Shipped"),
    )
    created_at = models.DateTimeField("date added", auto_now_add=True)
    updated_at = models.DateTimeField("last updated", auto_now=True)

    user = models.ForeignKey(
        AuthUser,
        related_name="products",
        related_query_name="product",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name="acquisitions",
        related_query_name="acquisition",
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=64, choices=STATUS, default="WISH_LIST")
    order = models.ForeignKey(
        Order, related_name="products", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.quantity} of {self.product.title}"

    def get_total_item_price(self):
        return self.quantity * self.product.price / 100

    def get_total_item_cost(self):
        return self.quantity * self.product.price
