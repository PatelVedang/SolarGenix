from django.urls import path

from auth_api.views import (
    ChangePasswordView,
    CreateCognitoGroupAPIView,
    ForgotPasswordView,
    GoogleSSOView,
    LogoutView,
    RefreshTokenView,
    ResendVerificationEmailView,
    ResetPasswordOTP,
    SendOTPView,
    User2FASetupView,
    User2FAVerifyView,
    UserLoginView,
    UserPasswordResetView,
    UserProfileView,
    UserRegistrationView,
    VerifyEmailView,
    VerifyOTPView,
    CognitoSyncTokensView,
)

urlpatterns = [
    path("auth/register", UserRegistrationView.as_view(), name="registration"),
    path("auth/login", UserLoginView.as_view(), name="login"),
    path("auth/login/google", GoogleSSOView.as_view(), name="google"),
    path("auth/me", UserProfileView.as_view(), name="me"),
    path(
        "auth/change-password",
        ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "auth/forgot-password",
        ForgotPasswordView.as_view(),
        name="forgot-password",
    ),
    path(
        "auth/reset-password/<str:token>",
        UserPasswordResetView.as_view(),
        name="reset-password",
    ),
    path("auth/refresh-token", RefreshTokenView.as_view(), name="refresh-token"),
    path(
        "auth/send-verification-email",
        ResendVerificationEmailView.as_view(),
        name="send-verification-email",
    ),
    path(
        "auth/verify-email/<str:token>", VerifyEmailView.as_view(), name="verify-email"
    ),
    path("auth/logout", LogoutView.as_view(), name="login-view"),
    path("auth/send-otp", SendOTPView.as_view(), name="send-otp-view"),
    path("auth/verify-otp", VerifyOTPView.as_view(), name="verify-otp-view"),
    path(
        "auth/reset-password-otp", ResetPasswordOTP.as_view(), name="reset-password-otp"
    ),
    path(
        "auth/cognito-sync-tokens",
        CognitoSyncTokensView.as_view(),
        name="cognito-sync-tokens",
    ),
    path(
        "auth/cognito/create-group",
        CreateCognitoGroupAPIView.as_view(),
        name="create-cognito-group",
    ),
    path("auth/2fa/setup/", User2FASetupView.as_view(), name="user-2fa-setup"),
    path("auth/2fa/verify/", User2FAVerifyView.as_view(), name="user-2fa-verify"),
]
