from django.shortcuts import render
from .models import Machine
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .tasks import scan
from .serializers import IpSerializer

@api_view(['POST'])
def scanHost(request):
    if request.method == 'POST':
        payload = IpSerializer(data = request.data) 
        if payload.is_valid(raise_exception=True):
            ip = request.data['ip']
            scan.delay(ip)
        return JsonResponse({"message":"success"})
