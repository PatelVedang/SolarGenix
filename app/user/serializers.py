from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.state import token_backend
from django.contrib.auth import authenticate
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(max_length=255, style={'input-type':'password'},write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
    
    def validate_password(self, value):
        return make_password(value)


class LoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        sr = UserSerializer(user)
        token['user'] = sr.data
        User.objects.filter(email=user).update(last_login=timezone.now())
        return token

    def validate(self, attrs):
        user = authenticate(email=attrs.get("email"), password = attrs.get("password"))
        if not user:
            raise serializers.ValidationError(
                'No active account found with the given credentials.'
            )
        return super().validate(attrs)

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = self.token_class(attrs['refresh'])
        data = super(CustomTokenRefreshSerializer, self).validate(attrs)
        data['refresh'] = str(refresh)
        decoded_payload = token_backend.decode(data['access'], verify=True)
        User.objects.filter(email=decoded_payload.get('user').get('email')).update(last_login=timezone.now())
        return data