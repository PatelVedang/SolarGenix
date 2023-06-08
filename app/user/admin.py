from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import User
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    add_fieldsets = (
        (None, {
            'fields': ('otp', 'otp_expires'),
        }),
    )
    fields = ('last_login', 'email', 'first_name', 'last_name', 'is_deleted', 'is_staff', 'is_superuser', 'otp', 'subscription')
    readonly_fields = ('id','otp','role')
    search_fields = ('first_name', 'last_name', 'email','subscription__plan_type')
    list_display = [
        'id', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'subscription', 'is_deleted'
    ]
admin.site.register(User, UserAdmin)