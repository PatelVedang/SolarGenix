from django.shortcuts import render
from .models import Machine
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .tasks import scan
from .serializers import ScannerSerializer, ScannerResponseSerializer
from rest_framework.response import Response
from rest_framework import viewsets, status
# from utils.make_response import response
from utils.make_response import response

class ScanViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = ScannerSerializer
    
    # API for create object
    def create(self, request, *args, **kwargs):
        # provide payload to serializer
        payload = self.serializer_class(data=request.data)

        #validate serializer with payload 
        if payload.is_valid(raise_exception=True):
            ip = request.data['ip']
            client = request.data['client']
            
            # Create record if it is not exist with provided ip and client  
            record = Machine.objects.filter(ip=ip, client=client)
            if not record.exists():
                payload.save()
            else:
                record.update(bg_task_status=True)
            # run background function 
            scan.delay(ip, client)
        return response(data = payload.data, status_code = status.HTTP_200_OK, message="host successfully added in queue")

    # API to retrive any scaned host
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ScannerResponseSerializer
        payload = super().retrieve(request, *args, **kwargs)
        print(payload,"=>>>retyriev")
        return response(data = payload.data, status_code = status.HTTP_200_OK, message="record found successfully")
