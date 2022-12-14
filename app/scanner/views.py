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

    def scanner(self, ip, client):
        #Create record if it is not exist with provided ip and client  
        record = Machine.objects.filter(ip=ip, client=client)
        if not record.exists():
            Machine.objects.create(ip=ip, client=client)
        else:
            record.update(bg_task_status=True)
        # run background function 
        scan.delay(ip, client)

    # API for create object
    def create(self, request, *args, **kwargs):
        # provide payload to serializer
        serializer = self.serializer_class(data=request.data)
        #validate serializer with given payload 
        if serializer.is_valid(raise_exception=True):
            
            ip_addresses = request.data['ip']
            client = request.data['client']

            if isinstance(ip_addresses, str):
                ip_addresses = [ip_addresses]

            for ip in ip_addresses:
                self.scanner(ip, client)

        custom_response = ScannerResponseSerializer(Machine.objects.filter(ip__in=ip_addresses, client=client), many=True)
        return response(data = custom_response.data, status_code = status.HTTP_200_OK, message="host successfully added in queue")


    # API to retrive any scaned host
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ScannerResponseSerializer
        serializer = super().retrieve(request, *args, **kwargs)
        return response(data = serializer.data, status_code = status.HTTP_200_OK, message="record found successfully")

    # API to get list of scan records
    # Query Params
    # client(client id), ip(ip in string), scanned(0 or 1), bg_task_status(0 or 1)
    def list(self, request, *args, **kwargs):
        result = Machine.objects.all()
        params = dict(request.query_params)
        if params.get('client'):
            result = result.filter(client=params.get('client')[0])
        if params.get('ip'):
            result = result.filter(ip=params.get('ip')[0])
        if params.get('tool'):
            result = result.filter(tool=params.get('tool')[0])

        try:
            if params.get('scanned'):
                if params.get('scanned')[0] in ['0','1']:
                    scanned = bool(int(params.get('scanned')[0]))
                    result = result.filter(scanned=scanned)
        except Exception as e:
            pass
        
        try:
            if params.get('bg_task_status'):
                if params.get('bg_task_status')[0] in ['0','1']:
                    bg_task_status = bool(int(params.get('bg_task_status')[0]))
                    result = result.filter(bg_task_status=bg_task_status)
        except Exception as e:
            pass

        message = "record found successfully"
        if not result:
            message = "record not found"
    
        self.serializer_class = ScannerResponseSerializer
        serializer = self.serializer_class(result, many=True)
        return response(data = serializer.data, status_code = status.HTTP_200_OK, message=message)
    