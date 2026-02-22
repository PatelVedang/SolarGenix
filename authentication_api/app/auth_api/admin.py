from core.models import GroupProfile, Token, User
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import render



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


def clean_group_name(name):
    return name.replace(" ", "_")


class SoftDeleteAdminMixin(admin.ModelAdmin):
    """Mixin to add soft delete and recover actions to the admin."""

    actions = ["soft_delete", "soft_delete_recover", "hard_delete_selected"]

    def soft_delete(self, request, queryset):
        """Soft delete selected items. After soft deleting of user which is show in database and admin panel only soft deleted user can not perform the any kind of task in website"""
        for user in queryset:
            user.is_deleted = True
            user.is_active = False
            user.save()

            # Delete related tokens
            Token.objects.filter(user=user).delete()

        self.message_user(
            request,
            f"{queryset.count()} item(s) soft deleted and related tokens deleted.",
        )

    def soft_delete_recover(self, request, queryset):
        """Recover selected soft deleted items. After recovering the user, the user can perform the task in website"""
        for user in queryset:
            user.is_deleted = False
            user.is_active = True
            user.save()

        self.message_user(request, f"{queryset.count()} item(s) restored.")

    def hard_delete_selected(self, request, queryset):
        """Hard delete selected items using Django default. This will permanently delete the user and their tokens from the database also"""
        return admin.actions.delete_selected(self, request, queryset)

    hard_delete_selected.short_description = "Hard delete"


class AssignGroupForm(forms.Form):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(), required=True, label="Select group to assign"
    )


class UserModelAdmin(BaseUserAdmin, SoftDeleteAdminMixin):
    # The forms to add and change user instances.
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin.
    # that reference specific fields on auth.User.
    def get_queryset(self, request):
        # Use the unfiltered manager in admin
        return self.model.default.all()

    actions = ["soft_delete", "soft_delete_recover", "assign_group_to_selected_users"]

    list_display = [
        "id",
        "username",
        "first_name",
        "email",
        "phone_number",
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
        ("Personal info", {"fields": ["first_name", "phone_number"]}),
        (
            "Permissions",
            {
                "fields": [
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "is_email_verified",
                    "is_deleted",
                    "groups",
                ]
            },
        ),
        ("Important dates", {"fields": ["last_login"]}),
    ]
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

    def save_related(self, request, form, formsets, change):
        """Override save_related to handle related objects synchronization."""
        super().save_related(request, form, formsets, change)

    def assign_group_to_selected_users(self, request, queryset):
        """Assign a group to selected users in the admin interface.
        This action allows admins to assign a group to multiple users at once."""
        if "apply" in request.POST:
            form = AssignGroupForm(request.POST)
            if form.is_valid():
                group = form.cleaned_data["group"]
                added_users = 0
                for user in queryset:
                    user.groups.add(group)
                    added_users += 1
                if added_users:
                    self.message_user(
                        request,
                        f"Successfully added {added_users} users to group '{group.name}'.",
                    )
                return None
        else:
            form = AssignGroupForm()
        return render(
            request,
            "admin/assign_group.html",
            context={
                "users": queryset,
                "form": form,
                "action": "assign_group_to_selected_users",
                "title": "Assign Group to Selected Users",
            },
        )

    def changelist_view(self, request, extra_context=None):
        """Override changelist_view to add groups to the context."""
        extra = extra_context or {}
        extra["groups"] = Group.objects.all()
        return super().changelist_view(request, extra_context=extra)

    def delete_model(self, request, obj):
        """Override delete_model."""
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Override delete_queryset."""
        super().delete_queryset(request, queryset)


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


class GroupProfileInline(admin.StackedInline):
    model = GroupProfile
    extra = 0


admin.site.unregister(Group)


class GroupAdmin(admin.ModelAdmin):
    """
    Custom Django admin class for managing Group objects with AWS Cognito synchronization.

    This admin class extends the default behavior to ensure that group creation, renaming, and deletion
    are mirrored in AWS Cognito when the AUTH_TYPE setting is set to "cognito". It handles the following:

    - On group creation: Creates a corresponding group in Cognito.
    - On group renaming: Renames the group in Cognito, migrates users to the new group, and handles exceptions if the group already exists.
    - On group deletion: Deletes the corresponding group in Cognito.
    - On bulk deletion: Deletes all corresponding groups in Cognito for the selected queryset.

    Additionally, it provides feedback to the admin user via Django's message framework for all Cognito-related operations.

    Attributes:
        list_display (list): Fields to display in the admin list view.
        search_fields (list): Fields to enable search functionality in the admin.
        inlines (list): Inline admin classes to display related models.

    Methods:
        save_model(request, obj, form, change): Handles saving and synchronizing group changes with Cognito.
        delete_model(request, obj): Handles deleting a group and its Cognito counterpart.
        delete_queryset(request, queryset): Handles bulk deletion of groups and their Cognito counterparts.
    """

    list_display = ["name"]
    search_fields = ["name"]
    inlines = [GroupProfileInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)


admin.site.register(Group, GroupAdmin)
