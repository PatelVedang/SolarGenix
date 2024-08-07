import requests
from rest_framework import serializers

from . import google
from .register import register_social_user


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    def validate_auth_token(self, auth_token):
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

        # if user_data['aud'] != os.environ.get('GOOGLE_CLIENT_ID'):

        # raise AuthenticationFailed('oops, who are you?')
        print(user_data, "============")
        # user_id = user_data["sub"]
        email = user_data["email"]
        name = user_data["name"]
        provider = "google"

        return register_social_user(provider=provider, email=email, name=name)


class ExchangeTokenSerializer(serializers.Serializer):
    authorization_code = serializers.CharField()

    def validate(self, data):
        authorization_code = data.get("authorization_code")

        if not authorization_code:
            raise serializers.ValidationError("Authorization code is required")

        return data

    def exchange_token(self):
        print("heyyyyyyy")
        authorization_code = self.validated_data["authorization_code"]
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": authorization_code,
            "client_id": "400347234091-gilju3sc5r32f37f6m4mq7j7loqspemk.apps.googleusercontent.com",
            "client_secret": "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",
            "redirect_uri": "https://developers.google.com/oauthplayground",
            "grant_type": "authorization_code",
        }
        print("fianlllllllllheyy")
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
