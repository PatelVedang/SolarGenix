from rest_framework import serializers
from auth_api.models import User, Token, BlacklistToken
from django.contrib.auth.hashers import make_password,check_password
import jwt
from datetime import datetime
from proj import settings

from auth_api.send_mail import send_email_async
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed

def get_tokens_for_user(user):
  
    refresh = RefreshToken.for_user(user)
    reset_token = RefreshToken.for_user(user)
    verify_token = RefreshToken.for_user(user)
    reset_token['token_type'] = 'reset'
    verify_token['token_type'] ='verify'
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'reset': str(reset_token),
        'verify': str(verify_token),
    }
    
    
def check_blacklist(jti) -> None:
    
    if BlacklistToken.objects.filter(jti=jti).exists():
        raise serializers.ValidationError("Token is blacklisted")
        
        
class UserRegistrationSerilizer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model=User
        fields=['email','name','password','password2','tc']
        # fields = '__all__'
        extra_kwargs={
                'password':{'write_only':True}
            }
    def validate(self, attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        
        if password != password2:
            raise serializers.ValidationError("Please Enter Same Password in Both Fields")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        user.is_active = False  # User is inactive until they verify their email
       
        # Generate JWT token
        tokens = get_tokens_for_user(user)
        verify_token = tokens['verify']
        token = jwt.decode(verify_token, settings.SECRET_KEY, algorithms=["HS256"])
        Token.objects.create(user=user,jti=token['jti'],token=verify_token,token_type='verify',expires_at=datetime.fromtimestamp(token['exp']))
        print("Token created",user.email)  
        # Send verification email
        send_email_async("Verify your account",f'Click the link below to verify your account : {verify_token}',settings.EMAIL_HOST_USER,[user.email])
        print("Verification email sent",user.email)
        return user
    
    
      
class UserLoginSerilizer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model=User
        fields=['email','password']
        
    def validate(self, attrs):
        email = attrs.get('email')
        user = User.objects.get(email=email)
        if not user.is_active:
            raise AuthenticationFailed("Email Not Verified")
        else:
            return attrs
        
        
        
        
class UserProfileSerilizer(serializers.ModelSerializer):
    class Meta:
        model=User  
        fields=['id','name','email']



class ChangePasswordEmailSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=255, style={'input-type':'password'},write_only=True)
    new_password = serializers.CharField(max_length=255, style={'input-type':'password'},write_only=True)
    confirm_new_password = serializers.CharField(max_length=255, style={'input-type':'password'},write_only=True)
    
    def validate(self, attrs):
        user = self.context['request'].user
        print("user", user)
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
        

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        print(password,password2)
        token = self.context.get('token')
        if password != password2:
            raise serializers.ValidationError("Password & Confirm Password Doesn't match ")
        try:
             payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
             check_blacklist(payload['jti'])
             token_object = Token.objects.get(jti=payload['jti'])
             user = token_object.user
             user.password = make_password(password)
             user.save()
             token_object.delete()
             return attrs
        except Token.DoesNotExist:
            raise serializers.ValidationError({"token":"Token not Found"})
        except User.DoesNotExist:
            raise serializers.ValidationError({"token": "User not Found"})
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError({"token": "Token has expired."})
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Invalid token")
        
        
        
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            tokens = get_tokens_for_user(user)
            reset_token = tokens['reset']
            payload = jwt.decode(reset_token, settings.SECRET_KEY, algorithms=["HS256"])
            print("jti",payload['jti'])
            print("token type ",payload['token_type'])
            Token.objects.create(user=user,jti=payload['jti'],token=reset_token,token_type='reset',expires_at=datetime.fromtimestamp(payload['exp']))
            reset_password_url = f'http://127.0.0.1:8000/api/user/reset-password/{reset_token}'
            message = (
                f"Hello {user.name},\n\n"
                "You have requested for password reset. Please click the link below to reset your password:\n\n"
                f"{reset_password_url}\n\n"
            )
            button_text = "Reset Password"
            # html_content = render_to_string('auth_api/reset_password_email.html', {'reset_password_url': reset_password_url, 'button_text': button_text})
            # text_content = strip_tags(html_content)
            email_subject = 'Reset Your Password'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_email_async(email_subject,message,email_from,recipient_list)
            return attrs
        else:
            raise serializers.ValidationError("Not Registered Email")    
        


class ResendResetTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            tokens = get_tokens_for_user(user)
            reset_token = tokens['reset']
            payload = jwt.decode(reset_token, settings.SECRET_KEY, algorithms=["HS256"])
            print("jti",payload['jti'])
            print("token type ",payload['token_type'])
            Token.objects.create(user=user,jti=payload['jti'],token=reset_token,token_type='reset',expires_at=datetime.fromtimestamp(payload['exp']))
            reset_password_url = f'http://127.0.0.1:8000/api/user/reset-password/{reset_token}'
            message = (
                f"Hello {user.name},\n\n"
                "You have requested for password reset. Please click the link below to reset your password:\n\n"
                f"{reset_password_url}\n\n"
            )
            button_text = "Reset Password"
            # html_content = render_to_string('auth_api/reset_password_email.html', {'reset_password_url': reset_password_url, 'button_text': button_text})
            # text_content = strip_tags(html_content)
            email_subject = 'Reset Your Password '
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_email_async(email_subject,message,email_from,recipient_list)
            return attrs
        else:
            raise serializers.ValidationError("Not Registered Email")   
        
        
                
class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        token = self.context.get('token')

        if password != password2:
            raise serializers.ValidationError("Password & Confirm Password Doesn't match ")

        try:
            # Decode the token using the correct secret and algorithm
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"]) 
            # check_blacklist(payload)
            check_blacklist(payload['jti'])
            token_object = Token.objects.get(jti=payload['jti'])
            user = token_object.user
            user.password = make_password(password)
            user.save()
            token_object.delete()
            return attrs

        except Token.DoesNotExist:
            raise serializers.ValidationError({"token":"Token not Found"})
        except User.DoesNotExist:
            raise serializers.ValidationError({"token": "User not Found"})
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError({"token": "Token has expired."})
        except jwt.InvalidTokenError:
            raise serializers.ValidationError("Invalid token")
