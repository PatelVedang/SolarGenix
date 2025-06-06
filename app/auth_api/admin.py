from app.auth_api.cognito import Cognito
from app.core.models.auth_api.auth import GroupProfile
from core.models import Token, User
from core.services.google_service import Google
from django.contrib import admin
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.actions import delete_selected
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.db import transaction
from django.shortcuts import render
from django.conf import settings

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
        super().save_related(request, form, formsets, change)
        obj = form.instance
        username = obj.email
        if obj.auth_provider == "cognito":
            try:
                with transaction.atomic():
                    cognito = Cognito()
                    for group_name in cognito.list_user_groups(username):
                        try:
                            cognito.remove_user_from_group(username, group_name)
                        except Exception as e:
                            self.message_user(
                                request,
                                f"Error removing user {username} from group '{group_name}': {str(e)}",
                                level="error",
                            )
                    for group in obj.groups.all():
                        try:
                            cognito.add_user_to_group(
                                username, clean_group_name(group.name)
                            )
                        except Exception as e:
                            self.message_user(
                                request,
                                f"Failed to add user {username} to Cognito group '{group.name}': {str(e)}",
                                level="error",
                            )
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to sync Cognito groups for {username}: {str(e)}",
                    level="error",
                )

    def assign_group_to_selected_users(self, request, queryset):
        if "apply" in request.POST:
            form = AssignGroupForm(request.POST)
            if form.is_valid():
                group = form.cleaned_data["group"]
                cognito = Cognito()
                added_users = 0
                errors = []
                clean_name = clean_group_name(group.name)
                for user in queryset:
                    user.groups.add(group)
                    if user.auth_provider == "cognito":
                        try:
                            cognito.add_user_to_group(user.email, clean_name)
                            added_users += 1
                        except Exception as e:
                            errors.append(f"User {user.email}: {str(e)}")
                if added_users:
                    self.message_user(
                        request,
                        f"Successfully added {added_users} users to group '{group.name}'.",
                    )
                for error in errors:
                    self.message_user(request, error, level=messages.ERROR)
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
        extra = extra_context or {}
        extra["groups"] = Group.objects.all()
        return super().changelist_view(request, extra_context=extra)

    def delete_model(self, request, obj):
        if obj.auth_provider == "cognito":
            try:
                Cognito().delete_user(obj.email)
                self.message_user(request, f"User '{obj.email}' deleted from Cognito.")
            except Exception as e:
                self.message_user(
                    request,
                    f"Error deleting Cognito user '{obj.email}': {str(e)}",
                    level=messages.ERROR,
                )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        cognito = Cognito()
        for obj in queryset:
            if obj.auth_provider == "cognito":
                try:
                    cognito.delete_user(obj.email)
                    self.message_user(
                        request, f"User '{obj.email}' deleted from Cognito."
                    )
                except Exception as e:
                    self.message_user(
                        request,
                        f"Error deleting Cognito user '{obj.email}': {str(e)}",
                        level=messages.ERROR,
                    )
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
    list_display = ["name"]
    search_fields = ["name"]
    inlines = [GroupProfileInline]

    def save_model(self, request, obj, form, change):
        if getattr(settings, "AUTH_TYPE", "").lower() == "cognito":
            try:
                cognito = Cognito()
                clean_name = clean_group_name(obj.name)
                if change:
                    old_group = Group.objects.get(pk=obj.pk)
                    old_name = clean_group_name(old_group.name)
                    if old_name != clean_name:
                        users_in_old_group = old_group.user_set.all()
                        cognito.delete_group(old_name)
                        try:
                            cognito.create_group(clean_name)
                            self.message_user(
                                request,
                                f"Group renamed in Cognito: '{old_name}' → '{clean_name}'",
                            )
                        except Exception as e:
                            if "GroupExistsException" in str(e):
                                self.message_user(
                                    request,
                                    f"Cognito group '{clean_name}' already exists.",
                                    level="warning",
                                )
                            else:
                                raise e
                        for user in users_in_old_group:
                            if user.auth_provider == "cognito":
                                try:
                                    cognito.add_user_to_group(user.email, clean_name)
                                except Exception as e:
                                    self.message_user(
                                        request,
                                        f"Failed to add user '{user.email}' to group '{clean_name}': {str(e)}",
                                        level="error",
                                    )
                else:
                    try:
                        cognito.create_group(clean_name)
                        self.message_user(
                            request, f"Cognito group '{clean_name}' created."
                        )
                    except Exception as e:
                        if "GroupExistsException" in str(e):
                            self.message_user(
                                request,
                                f"Cognito group '{clean_name}' already exists.",
                                level="warning",
                            )
                        else:
                            raise e
                super().save_model(request, obj, form, change)
            except Exception as e:
                self.message_user(
                    request,
                    f"Error syncing group '{obj.name}' with Cognito: {str(e)}",
                    level="error",
                )
        else:
            super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        clean_name = clean_group_name(obj.name)
        try:
            Cognito().delete_group(clean_name)
            self.message_user(request, f"Cognito group '{clean_name}' deleted.")
        except Exception as e:
            self.message_user(
                request,
                f"Error deleting Cognito group '{clean_name}': {str(e)}",
                level="error",
            )
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        cognito = Cognito()
        for obj in queryset:
            clean_name = clean_group_name(obj.name)
            try:
                cognito.delete_group(clean_name)
                self.message_user(request, f"Cognito group '{clean_name}' deleted.")
            except Exception as e:
                self.message_user(
                    request,
                    f"Error deleting Cognito group '{clean_name}': {str(e)}",
                    level="error",
                )
        super().delete_queryset(request, queryset)


admin.site.register(Group, GroupAdmin)
