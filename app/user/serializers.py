from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, TokenVerifySerializer
from rest_framework_simplejwt.state import token_backend
from django.contrib.auth import authenticate
from django.utils import timezone
from .tasks import send_email as background_send_mail
from utils.email import send_email
import random
from django.conf import settings
from datetime import datetime, timedelta
import re
import logging
logger = logging.getLogger('django')
import json
from django.contrib.auth.hashers import check_password
import threading
import uuid
from rest_framework_simplejwt.tokens import Token


# The RoleSerializer class is a serializer for the Role model, specifying the fields to be included in
# the serialized representation.
class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ['id', 'name', 'tool_access', 'target_access', 'client_name_access', 'scan_result_access', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        return super().validate(attrs)
    

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'last_login', 'email', 'is_deleted', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_verified', 'mobile_number', 'country_code', 'role', 'subscription', 'updated_at']


class RegisterSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(max_length=255, style={'input-type':'password'},write_only=True)
    confirm_password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'mobile_number', 'country_code', 'confirm_password', 'user_company', 'user_address']

    def validate(self, attrs):
        if (not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs['password'])) or (not re.search(settings.PASSWORD_VALIDATE_REGEX, attrs['confirm_password'])):
            raise serializers.ValidationError(
                settings.PASSWORD_VALIDATE_STRING
            )
        if (not re.search(settings.MOBILE_NUMBER_REGEX, attrs['mobile_number'])) or (not re.search(settings.COUNTRY_CODE_REGEX, attrs['country_code'])):
            raise serializers.ValidationError(
                settings.MOBILE_NUM_VALIDATE_STRING
            )
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        del attrs['confirm_password']
        attrs['password'] = make_password(attrs['password'])
        return super().validate(attrs)

    def create(self, validated_data):
        user = super().create(validated_data)
        admin = User.objects.get(id=1)

        role_id = Role.objects.filter(name='user')[0].id
        verification_token = str(uuid.uuid4())
        token_expiration = datetime.utcnow() + timedelta(hours=1)
        link="https://google.com"
        user_name = f"{user.first_name} {user.last_name}".upper()
        user_email = user.email
        user_created_at = user.created_at
        admin_name = f"{admin.first_name} {admin.last_name}".upper()
        

        # End-user mail confirmation
        email_body =  f'''
        Dear {user_name},

        Thank you for registering on Cyber Appliance. We're delighted to have you as a part of our community!

        Your account has been created, but it is currently pending activation by our admin team. Please allow us some time to review your account information.
        '''
        thread= threading.Thread(target=send_email,
                                kwargs={
                                    'subject':'Welcome to Cyber Appliance',
                                    'body':email_body,
                                    'sender':settings.BUSINESS_EMAIL,
                                    'recipients':[validated_data.get("email")],
                                    'fail_silently':False,
                                    'end_user_confimartion': True,
                                    'allow_html':True,
                                    'user_name':user_name
                                })
        thread.start()

        # Admin mail confirmation
        email_body =  f'''
        Hello {admin_name},

        A new user has registered on Cyber Appliance. Please review the user's information and consider activating their account. Here are the details:

        User Details:
        Name : {user_name}
        Email: {user_email}
        Registartion Date: {user_created_at}
        '''
        thread= threading.Thread(target=send_email,
                                kwargs={
                                    'subject': f'New User Registration: {user_name}',
                                    'body':email_body,
                                    'sender':settings.BUSINESS_EMAIL,
                                    'recipients':[admin.email],
                                    'fail_silently':False,
                                    'admin_user_confimartion': True,
                                    'allow_html':True,
                                    'user_name':user_name,
                                    'user_email':user_email,
                                    'user_created_at':user_created_at,
                                    'admin_name':admin_name
                                })
        thread.start()



        # email = validated_data.get("email")
        # link = f"{settings.PDF_DOWNLOAD_ORIGIN}/api/auth/verifyUserToken/{verification_token}"
        # email_body =  f'Please confirm that {email} is your email address by use this link {link} within 1 hour.'
        user.role_id = role_id
        # user.verification_token = verification_token
        # user.token_expiration = token_expiration
        user.save()
        
        # thread= threading.Thread(target=send_email,
        #                          kwargs={
        #                             'subject':'Verify User',
        #                             'body':email_body,
        #                             'sender':settings.BUSINESS_EMAIL,
        #                             'recipients':[validated_data.get("email")],
        #                             'fail_silently':False,
        #                             'link':link,
        #                             'email':email,
        #                             'allow_html':True
        #                         })
        # thread.start()
        return user


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
        if not user.is_verified:
            raise serializers.ValidationError(
                'Your account is not activated please contact to admin for further instructions!!'
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

from rest_framework_simplejwt.serializers import TokenVerifySerializer
from rest_framework_simplejwt.tokens import AccessToken
class CustomTokenVerifySerializer(TokenVerifySerializer):
    def validate(self, attrs):
        res =super().validate(attrs)
        token_payload = AccessToken(attrs['token'])
        user = token_payload['user']
        user = User.objects.get(id=user['id'])
        res = {
            'id': user.id, 
            'email': user.email, 
            'role': user.role.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_image':f'{settings.PDF_DOWNLOAD_ORIGIN}/media/{str(user.profile_image)}'
        }

        return res
    

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
        

        thread= threading.Thread(target=send_email,
                                 kwargs={
                                    'subject':'Password Reset',
                                    'body':email_body,
                                    'sender':settings.BUSINESS_EMAIL,
                                    'recipients':[validated_data.get("email")],
                                    'fail_silently':False,
                                    'otp':otp,
                                    'allow_html':True
                                })
        thread.start()
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

# The `UpdateProfileSerializer` class is a serializer in Python that updates user profiles and
# includes a nested serializer for the user's role.
class UpdateProfileSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    profile_image = serializers.ImageField(read_only=True)
    email = serializers.EmailField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'role', 'profile_image', 'email']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        return super().validate(attrs)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255, style={'input-type':'password'},write_only=True)
    new_password = serializers.CharField(max_length=255, style={'input-type':'password'},write_only=True)
    confirm_new_password = serializers.CharField(max_length=255, style={'input-type':'password'},write_only=True)
    
    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        user.set_password(validated_data['new_password'])
        user.save()
        return user
    

class ResendUserTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ["email"]
    
    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        email = attrs.get("email", "")
        user = User.objects.filter(email=email)
        if not user.exists():
            raise serializers.ValidationError("Something went wrong.")
        
        if user[0].is_verified:
            raise serializers.ValidationError("Account is already verified.")

        return attrs

    def create(self, validated_data):
        email = validated_data.get("email")
        user = User.objects.get(email=email)

        verification_token = str(uuid.uuid4())
        token_expiration = datetime.utcnow() + timedelta(hours=1)

        link = f"{settings.PDF_DOWNLOAD_ORIGIN}/api/auth/verifyUserToken/{verification_token}"
        email_body =  f'Please confirm that {email} is your email address by use this link {link} within 1 hour.'
        user.verification_token = verification_token
        user.token_expiration = token_expiration
        user.save()
        
        thread= threading.Thread(target=send_email,
                                 kwargs={
                                    'subject':'Verify User',
                                    'body':email_body,
                                    'sender':settings.BUSINESS_EMAIL,
                                    'recipients':[validated_data.get("email")],
                                    'fail_silently':False,
                                    'link':link,
                                    'email':email,
                                    'allow_html':True
                                })
        thread.start()
        return user
    

class VerifyUserTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    class Meta:
        fields = ["token"]
    
    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        token = attrs.get("token")
        user = User.objects.filter(verification_token=token)
        if not user.exists():
            raise serializers.ValidationError("Something went wrong.")
        
        if user[0].is_verified:
            raise serializers.ValidationError("Account is already verified.")
        

        datetime_diff = (datetime.strptime(user[0].token_expiration.strftime('%Y-%m-%d %H:%M:%S'),"%Y-%m-%d %H:%M:%S") - datetime.utcnow()).total_seconds()/60
        if datetime_diff <= 0:
            raise serializers.ValidationError("Invalid or expired verification token")

        return attrs

    def create(self, validated_data):
        token = validated_data.get("token")
        user = User.objects.get(verification_token=token)
        user.verification_token = None
        user.token_expiration = None
        user.is_verified = True
        user.save()
        return user
    

class EndUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = "__all__"