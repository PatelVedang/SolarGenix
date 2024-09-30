from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from django.conf import settings
import string

from auth_api.models import User
from utils.email import send_email


class Command(BaseCommand):
    help = "Create a superuser with an automatically generated password and send credentials via email."

    def generate_password(self):
        allowed_chars = string.ascii_letters + string.digits + string.punctuation
        return get_random_string(8, allowed_chars)

    def handle(self, *args, **options):
        email = settings.SUPERUSER_EMAIL

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f"A superuser already exists with email {email}.")
            )
            return

        password = self.generate_password()
        superuser = User.objects.create_superuser(email, password)

        email_context = {
            "subject": "Admin created successfully!",
            "user": superuser,
            "email": email,
            "password": password,
            "recipients": [email],
            "html_template": "superuser_created",
            "button_links": [f"{settings.FRONTEND_URL}/admin/"],
            "title": "Welcome on board!",
        }

        if not send_email(**email_context):
            self.stdout.write(
                self.style.ERROR(
                    "Failed to send email for superuser creation. Rolling back."
                )
            )
            superuser.delete()
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Superuser with email {email} created and email sent successfully."
            )
        )
