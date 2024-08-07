from auth_api.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


def register_social_user(provider, name, email):
    filtered_user_by_email = User.objects.filter(email=email)
    if filtered_user_by_email.exists():
        print("heyyy")
        if provider == filtered_user_by_email[0].auth_provider:
            registered_user = authenticate(email=email, password="123")
            return {"tokens": registered_user.tokens()}
        else:
            raise AuthenticationFailed(
                detail="Please continue your login using"
                + filtered_user_by_email[0].auth_provider
            )

    else:
        print("hiiii")
        user = {"email": email, "password": "123", "name": name, "tc": True}
        user = User.objects.create_user(**user)
        # user.is_verified = True
        user.auth_provider = provider
        user.save()
        print(email, "===EMAIL")
        new_user = authenticate(email=email, password="Parshva@123")
        print(new_user, "00000000000")
        return {"tokens": new_user.tokens()}
