from django.urls import path, include
from . import views
from rest_framework import routers
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
# router = routers.DefaultRouter()
# router.register('', views.AuthViews,basename='auth')

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('refreshToken', views.RefreshTokenView.as_view(), name='refreshToken'),
    path('verifyToken', views.VerifyTokenView.as_view(), name='verifyToken'),
]
