from django.contrib import admin
from .models import User
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    add_fieldsets = (
        (None, {
            'fields': ('otp', 'otp_expires'),
        }),
    )
    fields = ('last_login', 'email', 'first_name', 'last_name', 'is_deleted', 'is_staff', 'is_superuser', 'otp')
    readonly_fields = ('id','otp','role')
    search_fields = ('first_name', 'last_name', 'email',)
admin.site.register(User, UserAdmin)