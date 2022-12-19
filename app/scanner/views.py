from django.shortcuts import render
from .models import Machine
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .tasks import scan
from .serializers import ScannerSerializer, ScannerResponseSerializer
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter 
from utils.make_response import response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class ScanViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = ScannerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # search_fields = ['id', 'client', 'ip', 'scanned', 'bg_task_status', 'tool']
    filterset_fields = ['id', 'client', 'ip', 'scanned', 'bg_task_status', 'tool']
    

    def scanner(self, ip, client, tool):
        #Create record if it is not exist with provided ip and client  
        record = Machine.objects.filter(ip=ip, client=client, tool_id=tool)
        if not record.exists():
            Machine.objects.create(ip=ip, client=client, tool_id=tool)
        else:
            record.update(bg_task_status=True)
        # run background function 
        scan.delay(ip, client, tool)

    # API for create object
    def create(self, request, *args, **kwargs):
        # provide payload to serializer
        serializer = self.serializer_class(data=request.data)
        #validate serializer with given payload 
        if serializer.is_valid(raise_exception=True):
            ip_addresses = serializer.data.get('ip')
            client = serializer.data.get('client')
            tools = serializer.data.get('tools_id')
            if isinstance(ip_addresses, str):
                ip_addresses = [ip_addresses]
            if isinstance(tools, int):
                tools = [tools]
            for ip in ip_addresses:
                for tool in tools:
                    self.scanner(ip, client, tool)

        custom_response = ScannerResponseSerializer(Machine.objects.filter(ip__in=ip_addresses, tool_id__in=tools, client=client), many=True)
        return response(data = custom_response.data, status_code = status.HTTP_200_OK, message="host successfully added in queue")


    # API to retrive any scaned host
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ScannerResponseSerializer
        serializer = super().retrieve(request, *args, **kwargs)
        return response(data = serializer.data, status_code = status.HTTP_200_OK, message="record found successfully")

    # API to get list of scan records
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = ScannerResponseSerializer
        return super().retrieve(request, *args, **kwargs)

    # client(client id), ip(ip in string), scanned(0 or 1), bg_task_status(0 or 1), id, tool
    def list(self, request, *args, **kwargs):
        self.serializer_class = ScannerResponseSerializer
        data = super().list(request, *args, **kwargs)
        return response(data = data.data, status_code = status.HTTP_200_OK, message="record found successfully")