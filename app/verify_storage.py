import os
import sys

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")
sys.path.append(os.getcwd())

import django

django.setup()

from django.conf import settings


def test_stage(stage_name):
    print(f"\n--- Testing STAGE: {stage_name} ---")

    # Check settings
    if stage_name == "PROD":
        expected_storage = "utils.storage_backends.MediaStorage"
        is_prod = True
    else:
        expected_storage = "django.core.files.storage.FileSystemStorage"  # Django default when not overridden
        is_prod = False

    current_storage = getattr(
        settings, "DEFAULT_FILE_STORAGE", "django.core.files.storage.FileSystemStorage"
    )

    print(f"DEFAULT_FILE_STORAGE: {current_storage}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")

    if is_prod:
        if (
            "storages" in settings.INSTALLED_APPS
            and current_storage == expected_storage
        ):
            print("✅ PROD Storage Configuration is CORRECT")
        else:
            print("❌ PROD Storage Configuration is INCORRECT")
    else:
        if current_storage != "utils.storage_backends.MediaStorage":
            print(f"✅ {stage_name} Storage Configuration is CORRECT (Local)")
        else:
            print(
                f"❌ {stage_name} Storage Configuration is INCORRECT (Should be Local)"
            )


if __name__ == "__main__":
    # Note: Since settings are loaded once, we can only verify the current STAGE in the env
    current_stage = getattr(settings, "STAGE", "DEV")
    test_stage(current_stage)
