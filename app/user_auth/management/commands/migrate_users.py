import logging

from auth_api.models import User as AuthApiUser
from auth_api.serializers import UserDataMigrationSerializer
from django.core.management.base import BaseCommand
from user_auth.models import User as UserAuthUser

logger = logging.getLogger("django")


class Command(BaseCommand):
    help = "Transfer users from auth_api.User to user_auth.User using DRF serializer"

    def handle(self, *args, **kwargs):
        try:
            # Get all users from the old auth_api.User model
            auth_api_users = AuthApiUser.objects.all()
            auth_api_serialize_data = UserDataMigrationSerializer(
                auth_api_users, many=True
            )

            self.stdout.write(
                self.style.NOTICE(
                    f"Total old users found: {len(auth_api_serialize_data.data)}"
                )
            )
            for auth_api_user in auth_api_serialize_data.data:
                # Debug: print the user data being migrated
                self.stdout.write(self.style.NOTICE(f"Migrating user: {auth_api_user}"))

                # Serialize the data
                self.stdout.write(self.style.NOTICE(f"{auth_api_user}"))
                user_obj = UserAuthUser.objects.create(**auth_api_user)

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully migrated user: {user_obj.email}")
                )

            self.stdout.write(
                self.style.SUCCESS("User migration completed successfully!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))
