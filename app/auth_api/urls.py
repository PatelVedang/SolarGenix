from django.urls import path

from auth_api.views import (
    ChangePasswordView,
    ForgotPasswordView,
    GoogleSSOView,
    LogoutView,
    RefreshTokenView,
    ResendResetTokenView,
    ResendVerificationEmailView,
    UserLoginView,
    UserPasswordResetView,
    UserProfileView,
    UserRegistrationView,
    VerifyEmailView,
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
    path(
        "auth/resend-user-reset-token",
        ResendResetTokenView.as_view(),
        name="resend-user-reset-token",
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
]
