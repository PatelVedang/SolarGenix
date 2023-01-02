from django.shortcuts import render
from .models import Machine, Tool
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .tasks import scan
from .serializers import ScannerSerializer, ScannerResponseSerializer, ScannerQueueSerializer
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter 
from rest_framework.decorators import action
from utils.make_response import response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from braces.views import CsrfExemptMixin
from django.views.decorators.csrf import csrf_exempt

class ScanViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = ScannerSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # search_fields = ['id', 'client', 'ip', 'status', 'tool']
    filterset_fields = ['id', 'client', 'ip', 'status', 'tool']
    
    @swagger_auto_schema(
        method = 'post',
        request_body=ScannerQueueSerializer,
        operation_description= "Set machines in queue.",
        operation_summary="API to add machines in queue for scanning."

    )
    @action(methods=['POST'], detail=False, url_path="add-in-queue")
    def scanner(self, request, *args, **kwargs):
        """
        It takes a list of machine ids, and for each machine id, it calls the scan function in the
        tasks.py file
        
        :param request: The request object
        """
        self.serializer_class = ScannerQueueSerializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            machines_id = serializer.data.get('machines_id')
            for machine_id in machines_id: 
                scan.delay(machine_id)
        custom_response = ScannerResponseSerializer(Machine.objects.filter(id__in=machines_id), many=True)
        return response(data = custom_response.data, status_code = status.HTTP_200_OK, message="host successfully added in queue")

    # API for create object
    # @swagger_auto_schema(manual_parameters=[
    #     openapi.Parameter('ip', openapi.IN_BODY,type=openapi.TYPE_ARRAY, required=True, items=openapi.Items(type=openapi.TYPE_STRING)),
    # ], request_body= ScannerSerializer)
    @swagger_auto_schema(
        request_body=ScannerSerializer,
        operation_description= "Insert record in machine table.",
        operation_summary="API to insert new machines."
    )
    # @csrf_exempt
    def create(self, request, *args, **kwargs):
        # provide payload to serializer
        self.serializer_class = ScannerSerializer
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
            machines_list = []
            record_ids = []
            for ip in ip_addresses:
                for tool in tools:
                    # machines_list.append(Machine(ip=ip,client=client, tool= Tool(id=tool)))
                    obj = Machine.objects.create(ip=ip,client=client, tool= Tool(id=tool))
                    record_ids.append(obj.id)
                # Machine.objects.bulk_create(machines_list)
        custom_response = ScannerResponseSerializer(Machine.objects.filter(id__in=record_ids), many=True)
        return response(data = custom_response.data, status_code = status.HTTP_200_OK, message="host successfully added in database")


    # API to retrive any scaned host
    @swagger_auto_schema(
        operation_description= "Retrive machine with specified id.",
        operation_summary="API to rertive single machine record."
    )
    def retrieve(self, request, *args, **kwargs):
        """
        It overrides the default retrieve function of the generic viewset and returns a custom response
        
        :param request: The request object
        :return: The serializer.data is being returned.
        """
        self.serializer_class = ScannerResponseSerializer
        serializer = super().retrieve(request, *args, **kwargs)
        return response(data = serializer.data, status_code = status.HTTP_200_OK, message="record found successfully")

    @swagger_auto_schema(
        operation_description= "Get list of machines.",
        operation_summary="API to return list of machines.",
        operation_id=None
    )
    def list(self, request, *args, **kwargs):
        """
        A function that returns a response with the data and status code.
        
        :param request: The request object
        :return: The data is being returned in the form of a list.
        """
        self.serializer_class = ScannerResponseSerializer
        data = super().list(request, *args, **kwargs)
        return response(data = data.data, status_code = status.HTTP_200_OK, message="record found successfully")

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs):
        """
        The update function is a function that is used to update the data in the database
        
        :param request: The request object
        :return: The super class update method is being returned.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def partial_update(self, request, *args, **kwargs):
        """
        It's a function that takes in a request, and then passes that request to the super class's
        partial_update function
        
        :param request: The request object
        :return: The partial update method is being returned.
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(auto_schema=None)
    def destroy(self, request, *args, **kwargs):
        """
        It returns the superclass's destroy method, which is the same as the destroy method in the
        ModelViewSet class
        
        :param request: The request object
        :return: The super class destroy method is being returned.
        """
        return super().destroy(request, *args, **kwargs)