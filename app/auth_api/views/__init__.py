from .authentication_view import (
    LogoutView,
    UserLoginView,
    UserProfileView,
    UserRegistrationView,
)
from .cognito_view import CognitoSyncTokensView, CreateCognitoRoleAPIView
from .google_authentication_view import GoogleSSOView
from .password_view import ChangePasswordView, ForgotPasswordView, UserPasswordResetView
from .token_view import RefreshTokenView
from .two_fa_verification_view import User2FASetupView, User2FAVerifyView
from .verification_view import (
    ResendVerificationEmailView,
    ResetPasswordOTP,
    SendOTPView,
    VerifyEmailView,
    VerifyOTPView,
)


__all__ = [
    "LogoutView",
    "UserLoginView",
    "UserProfileView",
    "UserRegistrationView",
    "CognitoSyncTokensView",
    "CreateCognitoRoleAPIView",
    "GoogleSSOView",
    "ChangePasswordView",
    "ForgotPasswordView",
    "UserPasswordResetView",
    "RefreshTokenView",
    "User2FASetupView",
    "User2FAVerifyView",
    "ResendVerificationEmailView",
    "ResetPasswordOTP",
    "SendOTPView",
    "VerifyEmailView",
    "VerifyOTPView",
]