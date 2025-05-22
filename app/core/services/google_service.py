import logging
import requests
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework.exceptions import AuthenticationFailed
from utils.custom_exception import CustomValidationError

logger = logging.getLogger("django")

class Google:
    def verify_auth_token(self, auth_token):
        try:
            id_info = id_token.verify_oauth2_token(
                auth_token, google_requests.Request()
            )
            if "accounts.google.com" in id_info["iss"]:
                return id_info
        except:  # noqa: E722
            CustomValidationError("The token is either invalid or expired")

    def exchange_token(self, grant_type, token):
        """
        The function `exchange_token` exchanges a refresh token or authorization code for an access
        token using Google OAuth2.

        :param grant_type: Grant_type is a parameter that specifies the type of authorization grant
        being used. It can have values like "refresh_token" or "authorization_code" depending on the
        type of token exchange being performed
        :param token: The `token` parameter in the `exchange_token` function is the token that needs to
        be exchanged with Google for an access token. Depending on the `grant_type` specified, this
        token could be either a refresh token or an authorization code
        :return: The `exchange_token` method returns the JSON response from the POST request to the
        token URL if the response status code is 200.
        """
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "grant_type": grant_type,
        }

        if grant_type == "refresh_token":
            data["refresh_token"] = token
        elif grant_type == "authorization_code":
            data["code"] = token
            data["redirect_uri"] = "https://developers.google.com/oauthplayground"

        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Google exchange token error :", response.json())
            raise CustomValidationError("Opps, something went wrong")

    def validate_google_token(self, authorization_code):
        """
        The function `validate_google_token` exchanges an authorization code for tokens, verifies the
        auth token, and checks if the user is authenticated with Google.

        :param authorization_code: The `authorization_code` parameter is typically a temporary code
        obtained from the Google OAuth 2.0 authorization flow. This code is exchanged for access tokens
        that can be used to authenticate and authorize requests to Google APIs on behalf of a user
        :return: The function `validate_google_token` is returning the user data after validating the
        Google token.
        """
        tokens = self.exchange_token("authorization_code", authorization_code)
        auth_token = tokens.get("id_token")
        refresh_token = tokens.get("refresh_token")
        user_data = self.verify_auth_token(auth_token)
        try:
            user_data["sub"]
        except KeyError:
            raise CustomValidationError(
                "The token is invalid or expired. Please login again."
            )

        if user_data["aud"] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed("oops, who are you?")
        user_data["refresh_token"] = refresh_token
        return user_data

    def revoke_token(self, refresh_token):
        """
        The `revoke_token` function revokes an access token using a refresh token in Python.

        :param refresh_token: A refresh token is a special token used to obtain a new access token when
        the current access token expires. It is typically used in OAuth2 authentication flows to
        maintain continuous access to a resource without requiring the user to re-authenticate
        """
        tokens = self.exchange_token("refresh_token", refresh_token)
        new_access_token = tokens.get("access_token")
        revoke_url = "https://oauth2.googleapis.com/revoke"
        params = {"token": new_access_token}
        revoke_response = requests.post(revoke_url, params=params)
        if revoke_response.status_code == 200:
            logger.info("Access token revoked successfully.")
        else:
            logger.error(
                f"Failed to revoke access token: {revoke_response.status_code} {revoke_response.text}"
            )
