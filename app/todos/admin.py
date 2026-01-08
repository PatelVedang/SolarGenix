from django.contrib import admin
from core.models import Todos

@admin.register(Todos)
class TodosAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'inventory', 'available', 'published_date')
    search_fields = ('name', 'description', 'price', 'inventory', 'available', 'published_date')
