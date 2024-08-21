import requests
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Token, User


@receiver(pre_delete, sender=User)
def delete_google_app(sender, instance, **kwargs):
    try:
        # Fetch the google token associated with the user
        google_token = Token.objects.get(user=instance, token_type="google")

        # Refresh the access token
        url = "https://oauth2.googleapis.com/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": google_token.token,
        }
        response = requests.post(url, data=data)
        response_data = response.json()

        if response.status_code == 200:
            new_access_token = response_data["access_token"]
            print(f"New Access Token: {new_access_token}")
        else:
            raise Exception(f"Error refreshing token: {response_data}")

        # Revoke the new access token
        revoke_url = "https://oauth2.googleapis.com/revoke"
        params = {"token": new_access_token}
        revoke_response = requests.post(revoke_url, params=params)

        if revoke_response.status_code == 200:
            print("Access token revoked successfully.")
        else:
            print(
                f"Failed to revoke access token: {revoke_response.status_code} {revoke_response.text}"  # noqa: E501
            )

    except Token.DoesNotExist:
        print("Google token not found for this user.")
    except Exception as e:
        print(f"An error occurred: {e}")
