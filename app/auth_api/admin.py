from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from auth_api.models import User, Token


# Register your models here.
class UserModelAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = [
        "id",
        "email",
        "first_name",
        "is_superuser",
        "auth_provider",
        "is_active",
        "last_login",
    ]
    list_filter = ["is_superuser"]
    fieldsets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name"]}),
        ("Permissions", {"fields": ["is_superuser", "is_staff", "is_active"]}),
        ("Important dates", {"fields": ["last_login"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "password"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email", "id"]
    filter_horizontal = []


admin.site.register(User, UserModelAdmin)


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "token_type",
        "jti",
        "expire_at",
        "is_blacklist_at",
    )
    search_fields = ("user__email", "jti")
