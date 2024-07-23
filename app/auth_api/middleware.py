
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.exceptions import InvalidToken  
from rest_framework_simplejwt.tokens import UntypedToken
from .models import BlacklistToken
from django.http import JsonResponse

import logging
# from rest_framework.status import status
class CheckBlacklistMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header:
            try:
                token_type, token = auth_header.split()
                if token_type == 'Bearer':
                    validated_token = UntypedToken(token)
                    token_type = validated_token.get('token_type')
                    jti = validated_token.get('jti')
                    if BlacklistToken.objects.filter(jti=jti, token_type=token_type).exists():
                        return JsonResponse({'message': 'Token is Blacklisted'}, status=401)
            except InvalidToken as e:
                logging.error(f"Invalid token error: {e}")
                return JsonResponse({'message': 'Token is Blacklisted'}, status=401)
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                return JsonResponse({'detail': 'An error occurred'}, status=500)
