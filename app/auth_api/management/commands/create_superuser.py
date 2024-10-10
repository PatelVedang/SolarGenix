from auth_api.models import User
from django.conf import settings
from django.core.management.base import BaseCommand
from proj.models import generate_password  # Import the function
from utils.email import EmailService


class Command(BaseCommand):
    help = "Create a superuser with an automatically generated password and send credentials via email."

    def handle(self, *args, **options):
        email = settings.SUPERUSER_EMAIL

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f"A superuser already exists with email {email}.")
            )
            return

        password = generate_password()
        superuser = User.objects.create_superuser(email, password)

        email_service = EmailService(superuser)
        email_sent = email_service.send_email_superuser(password=password, email=email)
        if not email_sent:
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
