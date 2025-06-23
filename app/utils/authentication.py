import certifi
import requests
from auth_api.constants import AuthResponseConstants
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from jose import JWTError, jwt
from jose.utils import base64url_decode
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed as DRFAuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

User = get_user_model()


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that extends the base JWTAuthentication.
    Overrides:
        get_user(validated_token):
            Retrieves the user associated with the validated JWT token.
            Raises an AuthenticationFailed exception if the user is marked as deleted.
    Raises:
        AuthenticationFailed: If the user is marked as deleted.
    Returns:
        User instance if authentication is successful and the user is not deleted.
    """
 
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        # Check if the user is marked as deleted
        if user.is_deleted:
            raise AuthenticationFailed(
                _(AuthResponseConstants.ACCOUNT_DELETED), code="user_deleted"
            )

        return user


class CognitoAuthentication(BaseAuthentication):
    """
    Custom authentication class for Django REST Framework that validates JWT tokens issued by AWS Cognito.

    This class performs the following steps:
    1. Extracts the Bearer token from the Authorization header.
    2. Validates the token format and structure.
    3. Retrieves the JWT header and extracts the 'kid' (key ID).
    4. Fetches the JSON Web Key Set (JWKS) from the Cognito user pool to obtain the public key.
    5. Decodes and verifies the JWT signature using the public key.
    6. Validates the token's audience and issuer claims.
    7. Retrieves or creates a User object based on the Cognito 'sub' claim.

    Raises:
        DRFAuthenticationFailed: If the token is missing, malformed, invalid, or verification fails at any step.

    Returns:
        tuple: (user, token) if authentication is successful; otherwise, returns None.
    """

    def authenticate(self, request):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return None

        token = token.split(" ")[1]
        if len(token.split(".")) != 3:
            return None

        try:
            header = jwt.get_unverified_header(
                token
            )  # Get the JWT header without verifying the signature
            kid = header.get("kid")
            if not kid:
                raise DRFAuthenticationFailed("Missing 'kid' in token header")

            # Build issuer and JWKS URL based on user pool ID
            COGNITO_ISSUER = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}"
            jwks_url = f"{COGNITO_ISSUER}/.well-known/jwks.json"

            response = requests.get(
                jwks_url, verify=certifi.where()
            )  # Use certifi to verify SSL certificates

            if response.status_code != 200:
                raise DRFAuthenticationFailed(
                    AuthResponseConstants.INVALID_COGNITO_TOKEN
                    + f": JWKS fetch failed ({response.status_code})"
                )

            try:
                jwks_data = response.json()
            except ValueError:
                raise DRFAuthenticationFailed(
                    AuthResponseConstants.INVALID_COGNITO_TOKEN
                    + ": Invalid JSON from JWKS endpoint"
                )

            keys = jwks_data.get("keys", [])
            key = next((k for k in keys if k.get("kid") == kid), None)
            if not key:
                raise DRFAuthenticationFailed(
                    AuthResponseConstants.INVALID_COGNITO_TOKEN
                    + ": 'kid' not found in JWKS"
                )

            # Decode base64url-encoded exponent and modulus as bytes
            e_bytes = base64url_decode(key["e"].encode("utf-8"))
            n_bytes = base64url_decode(key["n"].encode("utf-8"))

            e = int.from_bytes(e_bytes, "big")
            n = int.from_bytes(n_bytes, "big")

            public_key = rsa.RSAPublicNumbers(e, n).public_key(default_backend())

            # Decode and verify JWT token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=settings.COGNITO_CLIENT_ID,
                issuer=COGNITO_ISSUER,
            )
            # Get or create user from payload email
            user, _ = User.objects.get_or_create(cognito_sub=payload["sub"])
            return (user, token)

        except (JWTError, KeyError, StopIteration) as e:
            raise DRFAuthenticationFailed(
                f"{AuthResponseConstants.INVALID_COGNITO_TOKEN}: {str(e)}"
            )
