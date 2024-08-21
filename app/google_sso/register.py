from auth_api.models import Token, User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


def register_social_user(provider, first_name, email, refresh_token):
    filtered_user_by_email = User.objects.filter(email=email)
    if filtered_user_by_email.exists():
        if provider == filtered_user_by_email[0].auth_provider:
            registered_user = authenticate(email=email, password="p@$$w0Rd")
            if registered_user:
                token_dict = dict(
                    Token.objects.filter(
                        user=registered_user, is_blacklisted=False, is_deleted=False
                    ).values_list("token_type", "token")
                )
                # Return structured response
                return {
                    "message": "Login done successfully!",
                    "data": {
                        "access": token_dict.get("access"),
                        "refresh": token_dict.get("refresh"),
                    },
                }
            else:
                raise AuthenticationFailed("Authentication failed after user creation.")
        else:
            raise AuthenticationFailed(
                detail="Please continue your login using"
                + filtered_user_by_email[0].auth_provider
            )

    else:
        user = {
            "email": email,
            "password": "p@$$w0Rd",
            "first_name": first_name,
        }
        user = User.objects.create_user(**user)
        user.auth_provider = provider
        user.save()
        new_user = authenticate(
            email=email, password="p@$$w0Rd", token_type="google", token=refresh_token
        )
        if new_user:
            token_dict = dict(
                Token.objects.filter(
                    user=new_user, is_blacklisted=False, is_deleted=False
                ).values_list("token_type", "token")
            )
            # Return structured response
            return {
                "message": "Login done successfully!",
                "data": {
                    "access": token_dict.get("access"),
                    "refresh": token_dict.get("refresh"),
                },
            }
        else:
            raise AuthenticationFailed("Authentication failed after user creation.")
