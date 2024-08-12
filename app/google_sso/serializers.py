import requests
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from . import google
from .register import register_social_user


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()
    refresh_token = serializers.CharField()

    # def validate_auth_token(self, auth_token, refresh_token):
    def validate(self, data):
        auth_token = data.get("auth_token")
        refresh_token = data.get("refresh_token")

        user_data = google.Google.validate(auth_token)
        # print(user_data,)
        try:
            user_data["sub"]
        except:  # noqa: E722
            import traceback

            traceback.print_exc()
            raise serializers.ValidationError(
                "The token is invalid or expired. Please login again."
            )

        if user_data["aud"] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed("oops, who are you?")
        # user_id = user_data["sub"]
        email = user_data["email"]
        first_name = user_data["name"]
        provider = "google"

        # return register_social_user(
        #     provider=provider,
        #     email=email,
        #     first_name=first_name,
        #     refresh_token=refresh_token,
        # )
        user_response = register_social_user(
            provider=provider,
            email=email,
            first_name=first_name,
            refresh_token=refresh_token,
        )
        return user_response


class ExchangeTokenSerializer(serializers.Serializer):
    print("nooooooooooooo")
    authorization_code = serializers.CharField()

    def validate(self, data):
        authorization_code = data.get("authorization_code")

        if not authorization_code:
            raise serializers.ValidationError("Authorization code is required")

        return data

    def exchange_token(self):
        authorization_code = self.validated_data["authorization_code"]
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": authorization_code,
            "client_id": "400347234091-gilju3sc5r32f37f6m4mq7j7loqspemk.apps.googleusercontent.com",
            "client_secret": "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",
            "redirect_uri": "https://developers.google.com/oauthplayground",
            "grant_type": "authorization_code",
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
