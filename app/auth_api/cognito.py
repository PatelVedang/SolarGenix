import base64
import hashlib
import hmac
import logging
import re
import traceback

import boto3
import jwt
import requests
from botocore.exceptions import ClientError
from core.models.auth_api.auth import Token
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed

from auth_api.constants import AuthResponseConstants

User = get_user_model()
logger = logging.getLogger(__name__)


class Cognito:
    def __init__(self):
        self.client = boto3.client(
            "cognito-idp",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    @staticmethod
    def decode_token(token: str):
        """Decode and return payload from a Cognito JWT token (signature not verified)."""
        try:
            return jwt.decode(
                token, options={"verify_signature": False}, algorithms=["RS256"]
            )
        except Exception as e:
            raise AuthenticationFailed(
                f"{AuthResponseConstants.INVALID_COGNITO_TOKEN}: {e}"
            )

    @staticmethod
    def exchange_code_for_tokens(code: str) -> dict:
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.COGNITO_CLIENT_ID,
            "client_secret": settings.COGNITO_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.COGNITO_REDIRECT_URI,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        cognito_token_url = f"{settings.COGNITO_DOMAIN}/oauth2/token"

        response = requests.post(cognito_token_url, data=data, headers=headers)
        if response.status_code != 200:
            raise Exception(AuthResponseConstants.COGNITO_TOKEN_EXCHANGE_FAILED)
        return response.json()

    @classmethod
    def logout_user(cls, user):
        """Simulates logout by removing locally stored Cognito tokens."""
        deleted, _ = Token.objects.filter(
            user=user,
            token_type__in=["access_token", "refresh_token", "id_token"],
            is_blacklist_at__isnull=True,
        ).delete()
        logger.info(f"[Cognito Logout] Removed {deleted} token(s) for user {user.id}")

    @staticmethod
    def is_valid_group_name(group_name: str) -> bool:
        """
        Validates the group name according to AWS Cognito naming rules.
        Allowed characters: letters, numbers, and `_+=,.@-`
        """
        return re.match(r"^[\w+=,.@-]+$", group_name) is not None

    def _validate_group_name(self, group_name: str):
        if not self.is_valid_group_name(group_name):
            raise ValueError(
                "Invalid group name. Allowed characters: letters, numbers, and _+=,.@-"
            )

    def add_user_to_role(self, username: str, group_name: str) -> bool:
        """Adds a user to a Cognito group."""
        self._validate_group_name(group_name)

        try:
            self.client.admin_add_user_to_group(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=username,
                GroupName=group_name,
            )
            return True
        except ClientError as e:
            logger.error(
                f"[Cognito] Failed to add user '{username}' to group '{group_name}': {e}"
            )
            return False
        except Exception as e:
            logger.error(f"[Cognito] Unexpected error: {e}\n{traceback.format_exc()}")
            return False

    def create_role(
        self,
        group_name: str,
        description: str = "",
        precedence: int = 0,
        role_arn: str = None,
    ):
        """Creates a new Cognito group."""
        self._validate_group_name(group_name)

        params = {
            "GroupName": group_name,
            "UserPoolId": settings.COGNITO_USER_POOL_ID,
            "Description": description,
            "Precedence": precedence,
        }
        if role_arn:
            params["RoleArn"] = role_arn

        try:
            return self.client.create_group(**params)
        except Exception as e:
            raise Exception(f"Failed to create group '{group_name}' in Cognito: {e}")

    def get_group(self, group_name: str):
        """Gets group details from Cognito."""
        self._validate_group_name(group_name)

        try:
            return self.client.get_group(
                GroupName=group_name,
                UserPoolId=settings.COGNITO_USER_POOL_ID,
            )
        except Exception as e:
            raise Exception(f"Failed to get group '{group_name}' from Cognito: {e}")

    def list_user_groups(self, username: str) -> list:
        """Lists all Cognito groups a user belongs to."""
        try:
            response = self.client.admin_list_groups_for_user(
                Username=username,
                UserPoolId=settings.COGNITO_USER_POOL_ID,
            )
            return [group["GroupName"] for group in response.get("Groups", [])]
        except self.client.exceptions.UserNotFoundException:
            logger.warning(f"[Cognito] User '{username}' not found in Cognito.")
            return []
        except ClientError as e:
            logger.error(f"[Cognito] Failed to list groups for user '{username}': {e}")
            return []
        except Exception as e:
            logger.error(f"[Cognito] Unexpected error: {e}\n{traceback.format_exc()}")
            return []

    def remove_user_from_role(self, username: str, group_name: str):
        """Removes a user from a specified Cognito group."""
        try:
            response = self.client.admin_remove_user_from_group(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=username,
                GroupName=group_name,
            )
            return response
        except self.client.exceptions.UserNotFoundException:
            raise Exception(f"User '{username}' not found in Cognito.")
        except self.client.exceptions.ResourceNotFoundException:
            raise Exception(f"Group '{group_name}' not found in Cognito.")
        except Exception as e:
            raise Exception(f"Error removing user from group: {e}")

    def delete_group(self, group_name: str):
        """Deletes a Cognito group."""
        self._validate_group_name(group_name)

        try:
            self.client.delete_group(
                GroupName=group_name,
                UserPoolId=settings.COGNITO_USER_POOL_ID,
            )
        except self.client.exceptions.ResourceNotFoundException:
            logger.warning(f"[Cognito] Group '{group_name}' not found for deletion.")
        except Exception as e:
            raise Exception(f"Failed to delete group '{group_name}' in Cognito: {e}")

    def delete_user(self, username: str):
        """Deletes a user from AWS Cognito."""
        try:
            self.client.admin_delete_user(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=username,
            )
            logger.info(f"[Cognito] Deleted user '{username}' from Cognito.")
        except self.client.exceptions.UserNotFoundException:
            logger.warning(f"[Cognito] User '{username}' not found for deletion.")
        except Exception as e:
            logger.error(f"[Cognito] Failed to delete user '{username}': {e}")
            raise Exception(f"Failed to delete user '{username}' in Cognito: {e}")

    def login(self, username: str, password: str) -> dict:
        """
        Authenticates a user with Cognito and returns tokens.
        """
        try:
            auth_params = {
                "USERNAME": username,
                "PASSWORD": password,
            }
            if (
                hasattr(settings, "COGNITO_CLIENT_SECRET")
                and settings.COGNITO_CLIENT_SECRET
            ):
                auth_params["SECRET_HASH"] = self.get_secret_hash(username)
            response = self.client.initiate_auth(
                ClientId=settings.COGNITO_CLIENT_ID,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters=auth_params,
            )
            return response["AuthenticationResult"]
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code == "NotAuthorizedException":
                raise Exception("Incorrect username or password.")
            if code == "UserNotConfirmedException":
                raise Exception("User is not confirmed.")
            raise Exception(f"Failed to login user '{username}' in Cognito: {e}")
        except Exception as e:
            raise Exception(f"Failed to login user '{username}' in Cognito: {e}")

    def get_secret_hash(self, username):
        message = username + settings.COGNITO_CLIENT_ID
        dig = hmac.new(
            str(settings.COGNITO_CLIENT_SECRET).encode("utf-8"),
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(dig).decode()

    def sign_up(self, username: str, password: str, user_attributes=None):
        """
        Registers a new user in Cognito.
        """
        if user_attributes is None:
            user_attributes = [{"Name": "email", "Value": username}]
        params = {
            "ClientId": settings.COGNITO_CLIENT_ID,
            "Username": username,
            "Password": password,
            "UserAttributes": user_attributes,
        }
        # Add SECRET_HASH if client secret is set
        if (
            hasattr(settings, "COGNITO_CLIENT_SECRET")
            and settings.COGNITO_CLIENT_SECRET
        ):
            params["SecretHash"] = self.get_secret_hash(username)
        try:
            return self.client.sign_up(**params)
        except Exception as e:
            raise Exception(f"Failed to sign up user '{username}' in Cognito: {e}")

    def admin_confirm_sign_up(self, username: str):
        """
        Confirms a Cognito user registration as an admin (bypasses OTP).
        """
        try:
            return self.client.admin_confirm_sign_up(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=username,
            )
        except Exception as e:
            raise Exception(f"Failed to confirm user '{username}' in Cognito: {e}")

    def admin_get_user(self, username: str):
        """
        Gets a user from Cognito User Pool.
        """
        try:
            return self.client.admin_get_user(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=username,
            )
        except self.client.exceptions.UserNotFoundException:
            raise Exception(f"User '{username}' not found in Cognito.")
        except Exception as e:
            raise Exception(f"Failed to get user '{username}' in Cognito: {e}")
