from django.contrib import admin

from .models import AddedProduct, Category, Order, Product, ShippingAddress

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ("name", "description")

    # def articles(self, obj):
    #     return obj.main_articles.count()

    # def applets(self, obj):
    #     return obj.main_applets.count()


# class ProductAdmin(admin.ModelAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)
admin.site.register(AddedProduct)
admin.site.register(ShippingAddress)
admin.site.register(Order)
