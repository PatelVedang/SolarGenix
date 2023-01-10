from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import viewsets
from .serializers import *
from rest_framework.decorators import action
from rest_framework import generics
from utils.make_response import response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        register_serializer = self.serializer_class(data=request.data)
        if register_serializer.is_valid(raise_exception=True):
            result = super().create(request, *args, **kwargs) 
            return response(data = result.data, status_code = status.HTTP_200_OK, message="user created successfully.")

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response(data = serializer.validated_data, status_code = status.HTTP_200_OK, message="user login successfully.")

class RefreshTokenView(TokenObtainPairView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return response(data = serializer.validated_data, status_code = status.HTTP_200_OK, message="user login successfully.")