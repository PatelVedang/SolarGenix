# Create Pacakge so we can access any service using just .services.<service_name>

from .cognito_service import (
    CognitoSyncTokensViewService,
    CreateCognitoRoleAPIViewService,
)
from .login_service import UserLoginViewService
from .register_service import UserRegisterViewService
from .totp_service import TOTPService
from .two_fa_verification_service import User2FAVerifyViewService

__all__ = [
    "UserLoginViewService",
    "UserRegisterViewService",
    "CognitoSyncTokensViewService",
    "CreateCognitoRoleAPIViewService",
    "User2FAVerifyViewService",
    "TOTPService",
]
