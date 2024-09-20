from django.contrib import admin
from .models import Demo


@admin.register(Demo)
class DemoAdmin(admin.ModelAdmin):
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
