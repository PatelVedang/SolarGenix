from django.urls import path
from auth_api.views import *

urlpatterns = [
    path('auth/register/',UserRegistrationView.as_view(),name="registration"),
    path('auth/login/',UserLoginView.as_view(),name="login"),
    path('auth/me/',UserProfileView.as_view(),name="profile"),
    path('auth/change-password/',ChangePassowordEmailView.as_view(),name="change-password-email"),
    # path('auth/reset-password/<str:token>/',UserChangePassword.as_view(),name="changepassword"),
    path('auth/forgot-password/',SendPasswordResetEmailView.as_view(),name="send-reset-password-email"),
    path('auth/reset-password/<str:token>/',UserPasswordResetView.as_view(),name="reset-password"),
    path('auth/resend-user-reset-token', ResendResetTokenView.as_view(), name='resend-user-reset-token'),
    # path("reset-password-view/<str:token>", reset_password, name='reset-password-view'),
    path('auth/verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),  
]


