from django.shortcuts import render
from .models import Machine, Tool
from user.models import User
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .tasks import scan
from .serializers import ScannerSerializer, ScannerResponseSerializer, AddInQueueByIdsSerializer, AddInQueueByNumbersSerializer, ToolSerializer
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter 
from rest_framework.decorators import action
from utils.make_response import response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import MachineRetrievePremission
from django.utils.decorators import method_decorator

@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['scan'], auto_schema=None))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['scan'], auto_schema=None))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['scan'], auto_schema=None))
class ScanViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = ScannerSerializer
    permission_classes = [IsAuthenticated, MachineRetrievePremission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # search_fields = ['id', 'ip', 'scan_by', 'status', 'tool']
    filterset_fields = ['id', 'ip', 'status', 'tool']
    
    @swagger_auto_schema(
        method = 'post',
        request_body=AddInQueueByIdsSerializer,
        operation_description= "Set machines in queue ids.",
        operation_summary="API to add machines in queue for scanning by ids.",
        tags=['Scan']

    )
    @action(methods=['POST'], detail=False, url_path="addByIds")
    def scan_by_ids(self, request, *args, **kwargs):
        self.serializer_class = AddInQueueByIdsSerializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            machines_id = serializer.data.get('machines_id')
            for machine_id in machines_id:
                scan.delay(machine_id)
        custom_response = ScannerResponseSerializer(Machine.objects.filter(id__in=machines_id), many=True)
        return response(status=True, data=custom_response.data, status_code=status.HTTP_200_OK, message="host successfully added in queue")
        
    @swagger_auto_schema(
        method = 'post',
        request_body=AddInQueueByNumbersSerializer,
        operation_description= "Set n numbers of machine .",
        operation_summary="API to add machines in queue for scanning by numbers.",
        tags=['Scan']

    )
    @action(methods=['POST'], detail=False, url_path="addByNumbers")
    def scan_by_numbers(self, request, *args, **kwargs):
        self.serializer_class = AddInQueueByNumbersSerializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # count
            n = serializer.data.get('count')
            if (not request.user.is_staff) and (not request.user.is_superuser):
                records = Machine.objects.filter(status=0, scan_by=request.user)[:n]
            else:
                records = Machine.objects.filter(status=0)[:n]
            for record in records: 
                scan.delay(record.id)
        custom_response = ScannerResponseSerializer(records, many=True)
        return response(status=True, data=custom_response.data, status_code=status.HTTP_200_OK, message="host successfully added in queue")

    # API for create object
    # @swagger_auto_schema(manual_parameters=[
    #     openapi.Parameter('ip', openapi.IN_BODY,type=openapi.TYPE_ARRAY, required=True, items=openapi.Items(type=openapi.TYPE_STRING)),
    # ], request_body= ScannerSerializer)
    @swagger_auto_schema(
        request_body=ScannerSerializer,
        operation_description= "Insert record in machine table.",
        operation_summary="API to insert new machines.",
        tags=['Scan']
    )
    def create(self, request, *args, **kwargs):
        # provide payload to serializer
        self.serializer_class = ScannerSerializer
        serializer = self.serializer_class(data=request.data)
        #validate serializer with given payload 
        if serializer.is_valid(raise_exception=True):
            ip_addresses = serializer.data.get('ip')
            tools = serializer.data.get('tools_id')
            scan_by = serializer.data.get('scan_by')
            if isinstance(ip_addresses, str):
                ip_addresses = [ip_addresses]
            if isinstance(tools, int):
                tools = [tools]
            record_ids = []
            for ip in ip_addresses:
                for tool in tools:
                    obj = Machine.objects.create(ip=ip, scan_by=request.user,tool=Tool(id=tool))
                    record_ids.append(obj.id)
        custom_response = ScannerResponseSerializer(Machine.objects.filter(id__in=record_ids), many=True)
        return response(status=True, data=custom_response.data, status_code=status.HTTP_200_OK, message="host successfully added in database")


    # API to retrieve any scaned host
    @swagger_auto_schema(
        operation_description= "Retrieve machine with specified id.",
        operation_summary="API to retrieve single machine record.",
        tags=['Scan']
    )
    def retrieve(self, request, *args, **kwargs):
        """
        It overrides the default retrieve function of the generic viewset and returns a custom response
        
        :param request: The request object
        :return: The serializer.data is being returned.
        """
        self.serializer_class = ScannerResponseSerializer
        serializer = super().retrieve(request, *args, **kwargs)
        return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    @swagger_auto_schema(
        operation_description= "Get list of machines.",
        operation_summary="API to return list of machines.",
        operation_id=None,
        tags=['Scan']
    )
    def list(self, request, *args, **kwargs):
        """
        A function that returns a response with the data and status code.
        
        :param request: The request object
        :return: The data is being returned in the form of a list.
        """
        if (not request.user.is_staff) and (not request.user.is_superuser):
            self.queryset = Machine.objects.filter(scan_by = request.user.id)
        self.serializer_class = ScannerResponseSerializer
        data = super().list(request, *args, **kwargs)
        return response(status=True, data=data.data, status_code=status.HTTP_200_OK, message="record found successfully")


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "List API.", operation_summary="API to get list of records."))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "Create API.", operation_summary="API to create new record."))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "Retrieve API.", operation_summary="API for retrieve single record by id."))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Tool'], auto_schema=None))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "Partial update API.", operation_summary="API for partial update record."))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "Delete API.", operation_summary="API to delete single record by id."))
class ToolViewSet(viewsets.ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def list(self, request, *args, **kwargs):
        serializer = super().list(request, *args, **kwargs)
        return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def create(self, request, *args, **kwargs):
         serializer = super().create(request, *args, **kwargs)
         return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully added in database.")

    def partial_update(self, request, *args, **kwargs):
        serializer = super().partial_update(request, *args, **kwargs)
        return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully updated in database.")

    def retrieve(self, request, *args, **kwargs):
        serializer = super().retrieve(request, *args, **kwargs)
        return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def destroy(self, request, *args, **kwargs):
        serializer = super().destroy(request, *args, **kwargs)
        return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="record deleted successfully")


     