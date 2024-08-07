import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.swagger import apply_swagger_tags

from .serializers import ExchangeTokenSerializer, GoogleSocialAuthSerializer


# Create your views here.
@apply_swagger_tags(
    tags=["Google"],
    method_details={
        "post": {
            "operation_description": "Google API",
            "request_body": GoogleSocialAuthSerializer,
            "operation_summary": "Dynamic POST method for login with Google",
        },
    },
)
class GoogleApi(APIView):
    serializer_class = GoogleSocialAuthSerializer

    def post(self, request):
        print(request.data, "requstttt")
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # serializer.is_valid(raise_exception=True)
            # print(serializer.data,"serializerrrrrr")
            print(serializer.validated_data, "validateddddddd")
            # data=serializer.validated_data
            # data = ((serializer.validated_data)['auth_token'])
            # data = ((serializer.validated_data))
            data = serializer.validated_data

            print(data, "dataaa")
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors)


@apply_swagger_tags(
    tags=["Google"],
    method_details={
        "post": {
            "operation_description": "Exchange Token for Google",
            "request_body": ExchangeTokenSerializer,
            "operation_summary": "Dynamic POST method to exchange token for Google",
        },
    },
)
class ExchangeTokenView(APIView):
    def post(self, request):
        serializer = ExchangeTokenSerializer(data=request.data)
        if serializer.is_valid():
            try:
                tokens = serializer.exchange_token()
                print("========", tokens)
                return Response(tokens, status=status.HTTP_200_OK)
            except requests.exceptions.HTTPError as e:
                return Response({"error": str(e)}, status=e.response.status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
