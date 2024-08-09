from auth_api.models import Token, User
from auth_api.serializers import get_tokens_for_user
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


def register_social_user(provider, name, email, refresh_token):
    filtered_user_by_email = User.objects.filter(email=email)
    if filtered_user_by_email.exists():
        if provider == filtered_user_by_email[0].auth_provider:
            registered_user = authenticate(email=email, password="123")
            return {"tokens": registered_user.tokens()}
        else:
            raise AuthenticationFailed(
                detail="Please continue your login using"
                + filtered_user_by_email[0].auth_provider
            )

    else:
        user = {"email": email, "password": "p@$$w0Rd", "name": name, "tc": True}
        user = User.objects.create_user(**user)
        user.auth_provider = provider
        user.save()
        new_user = authenticate(email=email, password="p@$$w0Rd")
        print("+++++", new_user)
        Token.objects.create(user=user, token_type="google", token=refresh_token)
        return {"tokens": get_tokens_for_user(new_user)}
        # return {"tokens": new_user.tokens()}
