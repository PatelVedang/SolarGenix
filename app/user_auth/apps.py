import importlib

from django.apps import AppConfig


class AuthApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_auth"

    def ready(self):
        importlib.import_module(f"{self.name}.signals")
