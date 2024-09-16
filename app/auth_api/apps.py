import importlib

from django.apps import AppConfig


class AuthApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_api"

    def ready(self):
        importlib.import_module(f"{self.name}.signals")
