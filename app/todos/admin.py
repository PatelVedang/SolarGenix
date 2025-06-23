from core.models import Todo
from django.contrib import admin


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    """Admin interface for managing Todo items."""

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
