from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "price",
        "inventory",
        "available",
        "published_date",
    )
    search_fields = ("name", "description", "price")
    list_filter = ("available", "published_date")
