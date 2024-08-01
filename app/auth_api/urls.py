from django.urls import path
from auth_api.views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    ChangePassowordView,
    SendPasswordResetEmailView,
    UserPasswordResetView,
    ResendResetTokenView,
    RefreshTokenView,
    ResendVerifyTokenView,
    VerifyEmailView,
    LogoutView,
)

urlpatterns = [
    path("auth/register/", UserRegistrationView.as_view(), name="registration"),
    path("auth/login/", UserLoginView.as_view(), name="login"),
    path("auth/me/", UserProfileView.as_view(), name="profile"),
    path(
        "auth/change-password/",
        ChangePassowordView.as_view(),
        name="change-password-email",
    ),
    path(
        "auth/forgot-password/",
        SendPasswordResetEmailView.as_view(),
        name="send-reset-password-email",
    ),
    path(
        "auth/reset-password/<str:token>/",
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
        "auth/resend-verify-token",
        ResendVerifyTokenView.as_view(),
        name="resend-verify-token",
    ),
    path(
        "auth/verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify-email"
    ),
    path("auth/logout/", LogoutView.as_view(), name="login-view"),
]
