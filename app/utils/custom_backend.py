from auth_api.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from utils.tokens import create_token
from django.contrib.auth.hashers import check_password


class EmailOnAuthBackend(BaseBackend):
    def authenticate(
        self, request, email=None, password=None, token_type=None, token=None, **kwargs
    ):
        UserModel = get_user_model()
        try:
            print("----000000---")
            user = UserModel.objects.get(email=email)
            if token_type == "google":
                print("hereeeeee")
                create_token(user, "google", token)
                # Token.objects.create(
                #     user=user,
                #     token=token,
                #     token_type=token_type,
                # )

            if not check_password(password, user.password):
                return None

            tokens = Token.objects.filter(
                user=user,
                token_type__in=["access", "refresh"],
                is_deleted=False,
            )
            for token in tokens:
                token.soft_delete()

            # Generate new tokens
            create_token(user, "access")
            create_token(user, "refresh")
            return user
        except UserModel.DoesNotExist:
            return None
