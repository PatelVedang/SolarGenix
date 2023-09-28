from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import User, Role
# Register your models here.
class RoleAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'tool_access', 'target_access', 'client_name_access', 'scan_result_access', 'is_deleted'
    ]

class UserAdmin(admin.ModelAdmin):
    add_fieldsets = (
        (None, {
            'fields': ('otp', 'otp_expires'),
        }),
    )
    fields = ('last_login', 'email', 'first_name', 'last_name', 'is_deleted', 'is_staff', 'is_superuser', 'otp', 'subscription', 'role', 'is_verified')
    readonly_fields = ('id','otp')
    search_fields = ('first_name', 'last_name', 'email','subscription__plan_type', 'role__name')
    list_display = [
        'id', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'subscription', 'is_deleted', 'is_active', 'role', 'is_verified'
    ]
admin.site.register(User, UserAdmin)
admin.site.register(Role, RoleAdmin)