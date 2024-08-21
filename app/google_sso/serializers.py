import requests
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from . import google
from .register import register_social_user


class GoogleSocialAuthSerializer(serializers.Serializer):
    authorization_code = serializers.CharField()

    def validate(self, data):
        authorization_code = data.get("authorization_code")
        if not authorization_code:
            raise serializers.ValidationError("Authorization code is required")

        tokens = self.exchange_token(authorization_code)
        return self.validate_google_token(tokens)

    def exchange_token(self, authorization_code):
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": authorization_code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": "https://developers.google.com/oauthplayground",
            "grant_type": "authorization_code",
        }
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def validate_google_token(self, tokens):
        auth_token = tokens.get("id_token")
        refresh_token = tokens.get("refresh_token")

        user_data = google.Google.validate(auth_token)
        try:
            user_data["sub"]
        except KeyError:
            raise serializers.ValidationError(
                "The token is invalid or expired. Please login again."
            )

        if user_data["aud"] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed("oops, who are you?")

        email = user_data["email"]
        first_name = user_data["name"]
        provider = "google"

        return register_social_user(
            provider=provider,
            email=email,
            first_name=first_name,
            refresh_token=refresh_token,
        )
