from django.contrib import admin
from django.contrib.admin.actions import delete_selected
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from auth_api.models import Token, User


class SoftDeleteAdminMixin(admin.ModelAdmin):
    actions = ["soft_delete", "soft_delete_recover"]

    def soft_delete(self, request, queryset):
        """Soft delete selected items."""
        queryset.update(is_deleted=True, is_active=False)  # Bulk update for efficiency
        self.message_user(request, f"{queryset.count()} items soft deleted.")

    def soft_delete_recover(self, request, queryset):
        """Recover selected soft deleted items."""
        queryset.update(is_deleted=False, is_active=True)
        self.message_user(request, f"{queryset.count()} items restored.")

    # Override the default delete action name
    delete_selected.short_description = "Hard delete"


# Register your models here.
class UserModelAdmin(BaseUserAdmin, SoftDeleteAdminMixin):
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
        "is_deleted",
    ]
    list_filter = ["is_superuser"]
    fieldsets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name"]}),
        (
            "Permissions",
            {"fields": ["is_superuser", "is_staff", "is_active", "is_deleted"]},
        ),
        ("Important dates", {"fields": ["last_login"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "password1", "password2"],
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
