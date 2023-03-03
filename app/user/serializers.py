from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.state import token_backend
from django.contrib.auth import authenticate
from django.utils import timezone
from .tasks import send_email
import random
from django.conf import settings
from datetime import datetime, timedelta
import re
from django.conf import settings
import logging
logger = logging.getLogger('django')
import json

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        return super().validate(attrs)


class RegisterSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(max_length=255, style={'input-type':'password'},write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        return super().validate(attrs)
    
    def validate_password(self, value):
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, value):
            raise serializers.ValidationError(
                settings.PASSWORD_VALIDATE_STRING
            )
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
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        refresh = self.token_class(attrs['refresh'])
        data = super(CustomTokenRefreshSerializer, self).validate(attrs)
        data['refresh'] = str(refresh)
        decoded_payload = token_backend.decode(data['access'], verify=True)
        User.objects.filter(email=decoded_payload.get('user').get('email')).update(last_login=timezone.now())
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ["email"]
    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        email = attrs.get("email", "")
        
        if User.objects.filter(email=email).exists():
            return attrs
        else:
            raise serializers.ValidationError({"email":"no user found with this email."})

    def create(self, validated_data):
        otp = random.randint(100000,999999)
        email_body =  f'OTP for password reset is {otp} do not share with anyone else. This OTP has a 15-minute expiration time.'
        user =  User.objects.filter(email=validated_data.get("email")).update(otp=otp, otp_expires=datetime.utcnow()+timedelta(minutes=15))
        
        send_email.delay(
                subject='Password Reset',
                body=email_body,
                sender=settings.EMAIL_HOST_USER,
                recipients=[validated_data.get("email")],
                fail_silently=False,
                otp = otp
            )
        return user


class OTPValidateSerializer(serializers.Serializer):
    otp = serializers.CharField()
    email = serializers.EmailField()
    
    class Meta:
        fields = ['phone_number','otp']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        otp = attrs.get('otp')
        email = attrs.get("email", "")
        user = User.objects.filter(otp=otp, email=email)
        if not user.exists():
            raise serializers.ValidationError("Invalid OTP.")
        
        datetime_diff = (datetime.strptime(user[0].otp_expires.strftime('%Y-%m-%d %H:%M:%S'),"%Y-%m-%d %H:%M:%S") - datetime.utcnow()).total_seconds()/60
        if datetime_diff <= 0:
            raise serializers.ValidationError('OTP expired.')
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)    
    class Meta:
        model = User
        fields = ["email", "otp", "password", "confirm_password"]
    
    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        email = attrs.get("email", "")
        otp = attrs.get('otp')
        user = User.objects.filter(otp=otp, email=email)
        if not user.exists():
            raise serializers.ValidationError("Something went wrong.")
        
        datetime_diff = (datetime.strptime(user[0].otp_expires.strftime('%Y-%m-%d %H:%M:%S'),"%Y-%m-%d %H:%M:%S") - datetime.utcnow()).total_seconds()/60
        if datetime_diff <= 0:
            raise serializers.ValidationError('OTP session expired.')
        
        if not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs.get('password')):
            raise serializers.ValidationError(
                settings.PASSWORD_VALIDATE_STRING
            )

        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError("Password and confirmation password were different.")
        return attrs

    def create(self, validated_data):
        otp = validated_data.get("otp")
        email = validated_data.get("email")

        password = validated_data.get("password")
        user = User.objects.get(email=email, otp=otp)
        user.otp = None
        user.otp_expires = None
        user.set_password(password)
        user.save()
        return user

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        return super().validate(attrs)