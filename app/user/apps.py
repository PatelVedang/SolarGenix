from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user"

    # def ready(self):
    #     from .signals import user_verify_signal, create_profile_image
