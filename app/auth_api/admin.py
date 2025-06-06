from core.models import Token, User
from core.services.google_service import Google
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# class SoftDeleteAdminMixin(admin.ModelAdmin):
#     actions = ["soft_delete", "soft_delete_recover"]

#     def soft_delete(self, request, queryset):
#         """Soft delete selected items."""
#         # Perform soft delete on the user
#         queryset.update(is_deleted=True, is_active=False)

#         # Delete tokens related to the soft-deleted users
#         for user in queryset:
#             tokens = Token.objects.filter(user=user)
#             for token in tokens:
#                 if token.token_type == "google":
#                     google = Google()
#                     google.revoke_token(token.jti)  # Revoke Google access
#                 token.hard_delete()  # Hard delete tokens after revoking
#         self.message_user(
#             request,
#             f"{queryset.count()} items soft deleted and related tokens deleted.",
#         )

#     def soft_delete_recover(self, request, queryset):
#         """Recover selected soft deleted items."""
#         queryset.update(is_deleted=False, is_active=True)
#         self.message_user(request, f"{queryset.count()} items restored.")

#     # Override the default delete action name
#     delete_selected.short_description = "Hard delete"


class SoftDeleteAdminMixin(admin.ModelAdmin):
    actions = ["soft_delete", "soft_delete_recover", "hard_delete_selected"]

    def soft_delete(self, request, queryset):
        """Soft delete selected items."""
        for user in queryset:
            user.is_deleted = True
            user.is_active = False
            user.save()

            # Revoke and delete tokens
            tokens = Token.objects.filter(user=user)
            for token in tokens:
                if token.token_type == "google":
                    google = Google()
                    google.revoke_token(token.jti)
                token.hard_delete()  # Or token.delete() if needed

        self.message_user(
            request,
            f"{queryset.count()} item(s) soft deleted and related tokens deleted.",
        )

    def soft_delete_recover(self, request, queryset):
        """Recover selected soft deleted items."""
        for user in queryset:
            user.is_deleted = False
            user.is_active = True
            user.save()

        self.message_user(request, f"{queryset.count()} item(s) restored.")

    def hard_delete_selected(self, request, queryset):
        """Hard delete selected items using Django default."""
        return admin.actions.delete_selected(self, request, queryset)

    hard_delete_selected.short_description = "Hard delete"


# Register your models here.
class UserModelAdmin(BaseUserAdmin, SoftDeleteAdminMixin):
    # The forms to add and change user instances.
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin.
    # that reference specific fields on auth.User.
    def get_queryset(self, request):
        # Use the unfiltered manager in admin
        return self.model.default.all()

    list_display = [
        "id",
        "email",
        "first_name",
        "is_superuser",
        "auth_provider",
        "is_active",
        "is_email_verified",
        "last_login",
        "is_deleted",
        "is_default_password",
    ]
    list_filter = ["is_superuser"]
    fieldsets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name"]}),
        (
            "Permissions",
            {
                "fields": [
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "is_email_verified",
                    "is_deleted",
                ]
            },
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
