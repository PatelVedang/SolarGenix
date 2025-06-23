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
        """
        Decodes a JWT token without verifying its signature.

        Args:
            token (str): The JWT token to decode.

        Returns:
            dict: The decoded token payload.

        Raises:
            AuthenticationFailed: If the token cannot be decoded.
        """
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
        """
        Exchanges an authorization code for access and refresh tokens from AWS Cognito.
        Args:
            code (str): The authorization code received from the Cognito authorization endpoint.
        Returns:
            dict: A dictionary containing the tokens and related information returned by Cognito.
        Raises:
            Exception: If the token exchange fails (i.e., response status code is not 200).
        """

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
        """
        Logs out the specified user by deleting all their active tokens of types 'access_token', 'refresh_token', and 'id_token' that have not been blacklisted.

        Args:
            user (User): The user instance whose tokens should be deleted.

        Returns:
            None

        Side Effects:
            Deletes relevant Token objects from the database and logs the number of tokens removed.
        """
        deleted, _ = Token.objects.filter(
            user=user,
            token_type__in=["access_token", "refresh_token", "id_token"],
            is_blacklist_at__isnull=True,
        ).delete()
        logger.info(f"[Cognito Logout] Removed {deleted} token(s) for user {user.id}")

    @staticmethod
    def is_valid_group_name(group_name: str) -> bool:
        return re.match(r"^[\w+=,.@-]+$", group_name) is not None

    def _validate_group_name(self, group_name: str):
        """
        Validates the provided group name against allowed characters.

        Args:
            group_name (str): The name of the group to validate.

        Raises:
            ValueError: If the group name contains invalid characters. Allowed characters are letters, numbers, and _+=,.@-
        """
        if not self.is_valid_group_name(group_name):
            raise ValueError(
                "Invalid group name. Allowed characters: letters, numbers, and _+=,.@-"
            )

    def add_user_to_role(self, username: str, group_name: str) -> bool:
        """
        Adds a user to a specified Cognito group (role).

        Args:
            username (str): The username of the user to add to the group.
            group_name (str): The name of the Cognito group to add the user to.

        Returns:
            bool: True if the user was successfully added to the group, False otherwise.

        Raises:
            ValueError: If the group name is invalid.

        Logs:
            Logs an error message if the operation fails due to a ClientError or any unexpected exception.
        """
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
        """
        Creates a new group (role) in the AWS Cognito User Pool.

        Args:
            group_name (str): The name of the group to create.
            description (str, optional): A description for the group. Defaults to "".
            precedence (int, optional): The precedence value of the group. Defaults to 0.
            role_arn (str, optional): The ARN of the IAM role to associate with the group. Defaults to None.

        Returns:
            dict: The response from the Cognito create_group API call.

        Raises:
            Exception: If the group creation fails, an exception is raised with details.
        """
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
        """
        Retrieve information about a specific group from AWS Cognito.

        Args:
            group_name (str): The name of the group to retrieve.

        Returns:
            dict: The response from Cognito containing group details.

        Raises:
            Exception: If the group cannot be retrieved from Cognito or if the group name is invalid.
        """
        self._validate_group_name(group_name)

        try:
            return self.client.get_group(
                GroupName=group_name,
                UserPoolId=settings.COGNITO_USER_POOL_ID,
            )
        except Exception as e:
            raise Exception(f"Failed to get group '{group_name}' from Cognito: {e}")

    def list_user_groups(self, username: str) -> list:
        """
        Retrieves the list of group names that a specified user belongs to in the Cognito User Pool.

        Args:
            username (str): The username of the user whose groups are to be listed.

        Returns:
            list: A list of group names the user is a member of. Returns an empty list if the user is not found,
                  if there is a client error, or if an unexpected exception occurs.

        Logs:
            - A warning if the user is not found in Cognito.
            - An error if there is a client error or an unexpected exception.
        """
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
        """
        Removes a user from a specified Cognito group.

        Args:
            username (str): The username of the user to be removed from the group.
            group_name (str): The name of the Cognito group from which the user will be removed.

        Returns:
            dict: The response from the Cognito client after attempting to remove the user from the group.

        Raises:
            Exception: If the user is not found in Cognito.
            Exception: If the group is not found in Cognito.
            Exception: For any other errors encountered during the removal process.
        """
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
        """
        Deletes a group from the Cognito user pool.

        Args:
            group_name (str): The name of the group to be deleted.

        Raises:
            Exception: If the group deletion fails for reasons other than the group not being found.

        Logs:
            A warning if the specified group does not exist in the Cognito user pool.
        """
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
        """
        Deletes a user from the AWS Cognito User Pool.

        Args:
            username (str): The username of the user to be deleted.

        Raises:
            Exception: If deletion fails for reasons other than the user not being found.

        Logs:
            - Info log if the user is successfully deleted.
            - Warning log if the user is not found.
            - Error log if deletion fails due to other exceptions.
        """
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
        Authenticate a user with AWS Cognito using the provided username and password.

        Args:
            username (str): The username of the user attempting to log in.
            password (str): The password of the user.

        Returns:
            dict: The authentication result returned by Cognito, typically containing tokens.

        Raises:
            Exception: If the username or password is incorrect.
            Exception: If the user is not confirmed.
            Exception: For any other errors encountered during authentication.
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
        """
        Generates a secret hash for AWS Cognito authentication.
        This method creates a base64-encoded HMAC-SHA256 hash using the provided username,
        the Cognito client ID, and the Cognito client secret. The resulting hash is used
        as the 'SECRET_HASH' parameter when authenticating with AWS Cognito.
        Args:
            username (str): The username for which to generate the secret hash.
        Returns:
            str: The base64-encoded secret hash string.
        """

        message = username + settings.COGNITO_CLIENT_ID
        dig = hmac.new(
            str(settings.COGNITO_CLIENT_SECRET).encode("utf-8"),
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(dig).decode()

    def sign_up(self, username: str, password: str, user_attributes=None):
        """
        Registers a new user in AWS Cognito with the provided username, password, and optional user attributes.
        Args:
            username (str): The username (typically an email) for the new user.
            password (str): The password for the new user.
            user_attributes (list[dict], optional): A list of user attribute dictionaries to associate with the user.
                Each dictionary should have "Name" and "Value" keys. Defaults to setting the "email" attribute to the username.
        Returns:
            dict: The response from the Cognito `sign_up` API call.
        Raises:
            Exception: If the sign-up process fails, an exception is raised with details.
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
        Confirms a user's sign-up in the Cognito User Pool as an administrator.

        Args:
            username (str): The username of the user to confirm.

        Returns:
            dict: The response from the Cognito admin_confirm_sign_up API call.

        Raises:
            Exception: If the confirmation fails, an exception is raised with details.
        """
        try:
            return self.client.admin_confirm_sign_up(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=username,
            )
        except Exception as e:
            raise Exception(f"Failed to confirm user '{username}' in Cognito: {e}")

    def admin_get_user(self, username: str):
        try:
            return self.client.admin_get_user(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=username,
            )
        except self.client.exceptions.UserNotFoundException:
            raise Exception(f"User '{username}' not found in Cognito.")
        except Exception as e:
            raise Exception(f"Failed to get user '{username}' in Cognito: {e}")
