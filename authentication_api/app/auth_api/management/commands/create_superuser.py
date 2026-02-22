from core.models import User
from django.conf import settings
from django.core.management.base import BaseCommand
from proj.models import generate_password  # Import the function


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

        self.stdout.write(
            self.style.SUCCESS(
                f"Superuser with email {email} created successfully."
            )
        )
