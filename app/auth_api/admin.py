from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from auth_api.models import User,Token,BlacklistToken
# from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
# Register your models here.
class UserModelAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["id","email", "name","is_superuser"]
    list_filter = ["is_superuser"]
    fieldsets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["name"]}),
        ("Permissions", {"fields": ["is_superuser", "is_staff"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name","password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email","id"]
    filter_horizontal = []
    
admin.site.register(User, UserModelAdmin)

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token_type', 'jti', 'expires_at', 'is_blacklisted')
    search_fields = ('user__email', 'jti')
@admin.register(BlacklistToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ('jti', 'token_type', 'blacklisted_on')
