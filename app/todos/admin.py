from django.contrib import admin
from core.models import Todo

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'inventory', 'available', 'published_date')
    search_fields = ('name', 'description', 'price', 'inventory', 'available', 'published_date')
