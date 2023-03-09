from django.shortcuts import render
from .models import Target, Tool, TargetLog
from user.models import User
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .tasks import scan
from .serializers import ScannerSerializer, ScannerResponseSerializer, AddInQueueByIdsSerializer, AddInQueueByNumbersSerializer, ToolSerializer, ToolPayloadSerializer
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.filters import SearchFilter 
from rest_framework.decorators import action
from utils.make_response import response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAdminUser
from .permissions import MachineRetrievePremission, IsAdminUserOrList, IsAuthenticated
from django.utils.decorators import method_decorator
from utils.pdf import PDF
from django.shortcuts import get_object_or_404
from utils.message import send
from web_socket.serializers import SendMessageSerializer
import time
from datetime import datetime
from django.conf import settings
import logging
logger = logging.getLogger('django')

import json
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Targets'], auto_schema=None))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Targets'], auto_schema=None))
class ScanViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = ScannerSerializer
    permission_classes = [IsAuthenticated, MachineRetrievePremission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['ip', 'scan_by__first_name', 'scan_by__last_name', 'tool__tool_name', 'updated_at']
    filterset_fields = ['id', 'ip', 'status', 'tool']
    ordering_fields = ['tool__tool_name', 'ip', 'id', 'created_at', 'updated_at', 'status']

    @swagger_auto_schema(
        method = 'post',
        request_body=AddInQueueByIdsSerializer,
        operation_description= "Set targets in queue ids.",
        operation_summary="API to add targets in queue for scanning by ids.",
        tags=['Targets']

    )
    @action(methods=['POST'], detail=False, url_path="addByIds")
    def scan_by_ids(self, request, *args, **kwargs):
        """
        It adds the target to the queue by list of ids.
        
        :param request: The request object
        :return: The response is a list of targets.
        """
        self.serializer_class = AddInQueueByIdsSerializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            targets_id = serializer.data.get('targets_id')
            for target_id in targets_id:
                target_obj = Target.objects.get(id=target_id)
                tool_time_limit = target_obj.tool.time_limit
                scan.apply_async(args=[], kwargs={'id':target_id, 'time_limit':tool_time_limit, 'token':request.headers.get('Authorization')}, time_limit=tool_time_limit+10, ignore_result=True)
        custom_response = ScannerResponseSerializer(Target.objects.filter(id__in=targets_id), many=True)
        return response(status=True, data=custom_response.data, status_code=status.HTTP_200_OK, message="host successfully added in queue")
        
    @swagger_auto_schema(
        method = 'post',
        request_body=AddInQueueByNumbersSerializer,
        operation_description= "Set n numbers of machine .",
        operation_summary="API to add targets in queue for scanning by numbers.",
        tags=['Targets']

    )
    @action(methods=['POST'], detail=False, url_path="addByNumbers")
    def scan_by_numbers(self, request, *args, **kwargs):
        """
        It adds the n number targets to the queue.
        
        :param request: The request object
        :return: The response is a list of dictionaries.
        """
        self.serializer_class = AddInQueueByNumbersSerializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # count
            n = serializer.data.get('count')
            if (not request.user.is_staff) and (not request.user.is_superuser):
                records = Target.objects.filter(status=0, scan_by=request.user)[:n]
            else:
                records = Target.objects.filter(status=0)[:n]
            for record in records:
                tool_time_limit = record.tool.time_limit
                scan.apply_async(args=[], kwargs={'id':record.id, 'time_limit':tool_time_limit, 'token':request.headers.get('Authorization')}, time_limit=tool_time_limit+10, ignore_result=True)
        custom_response = ScannerResponseSerializer(records, many=True)
        return response(status=True, data=custom_response.data, status_code=status.HTTP_200_OK, message="host successfully added in queue")

    # API for create object
    # @swagger_auto_schema(manual_parameters=[
    #     openapi.Parameter('ip', openapi.IN_BODY,type=openapi.TYPE_ARRAY, required=True, items=openapi.Items(type=openapi.TYPE_STRING)),
    # ], request_body= ScannerSerializer)
    @swagger_auto_schema(
        request_body=ScannerSerializer,
        operation_description= "Insert record in machine table.",
        operation_summary="API to insert new targets.",
        tags=['Targets']
    )
    def create(self, request, *args, **kwargs):
        """
        It creates a target in the database.
        
        :param request: The request object
        """
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
                    obj = Target.objects.create(ip=ip, scan_by=request.user,tool=Tool(id=tool))
                    record_ids.append(obj.id)
        custom_response = ScannerResponseSerializer(Target.objects.filter(id__in=record_ids), many=True)
        return response(status=True, data=custom_response.data, status_code=status.HTTP_200_OK, message="host successfully added in database")


    # API to retrieve any scaned host
    @swagger_auto_schema(
        operation_description= "Retrieve machine with specified id.",
        operation_summary="API to retrieve single machine record.",
        tags=['Targets']
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
        operation_description= "Get list of targets.",
        operation_summary="API to return list of targets.",
        operation_id=None,
        tags=['Targets']
    )
    def list(self, request, *args, **kwargs):
        """
        A function that returns a response with the data and status code.
        
        :param request: The request object
        :return: The data is being returned in the form of a list.
        """
        if (not request.user.is_staff) and (not request.user.is_superuser):
            self.queryset = Target.objects.filter(scan_by = request.user.id)
        self.serializer_class = ScannerResponseSerializer
        data = super().list(request, *args, **kwargs)
        return response(status=True, data=data.data, status_code=status.HTTP_200_OK, message="record found successfully")

    @swagger_auto_schema(
        method = 'get',
        operation_description= "Generate pdf from a scan result. And provide url of pdf as aresponse.",
        operation_summary="API to generate pdf url.",
        request_body=None,
        tags=['Targets']

    )
    @action(methods=['GET'], detail=True, url_path="generatePDF")
    def generate_pdf(self, request, *args, **kwargs):
        """
        It takes the id of the user and the id of the response and generates a pdf file url
        
        :param request: The request object
        :return: A PDF file url
        """
        self.serializer_class = ScannerResponseSerializer
        serializer = super().retrieve(request, *args, **kwargs)
        pdf= PDF()

        pdf_path, pdf_name, file_url = pdf.generate(request.user.id, serializer.data.get('id'))
        
        data = {
            'file_path':file_url
        }
        TargetLog.objects.create(target=Target(serializer.data.get('id')), action=6)
        return response(status=True, data=data, status_code=status.HTTP_200_OK, message="PDF generated successfully")
    
    @swagger_auto_schema(
        method = 'get',
        operation_description= "Generate pdf from a scan result. And provide pdf file as a response.",
        operation_summary="API to provide pdf file.",
        request_body=None,
        tags=['Targets']

    )
    @action(methods=['GET'], detail=True, url_path="fakePDFGenerator")
    def generate_fake_pdf(self, request, *args, **kwargs):
        """
        It takes a target id, retrieves the target data from the database, generates a PDF file from the
        data, and returns the PDF file to the user
        
        :param request: The request object
        :return: The PDF file is being returned.
        """
        self.serializer_class = ScannerResponseSerializer
        serializer = super().retrieve(request, *args, **kwargs)
        pdf= PDF()
        pdf_path, pdf_name, file_url = pdf.generate(request.user.id, serializer.data.get('id'))
        FilePointer = open(pdf_path,"rb")
        response = HttpResponse(FilePointer,content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={pdf_name}'
        return response

    @swagger_auto_schema(
        method = 'get',
        operation_description= "Generate html content from a scan result. And provide html content as a response.",
        operation_summary="API to generate html content.",
        request_body=None,
        tags=['Targets']

    )
    @action(methods=['GET'], detail=True, url_path="generateHTML")
    def generate_html(self, request, *args, **kwargs):
        """
        It takes a target id, generates a PDF, and returns the HTML content of the PDF
        
        :param request: The request object
        :return: The HTML content of the report
        """
        self.serializer_class = ScannerResponseSerializer
        serializer = super().retrieve(request, *args, **kwargs)
        pdf= PDF()
        html_data = pdf.generate(request.user.id, serializer.data.get('id'), generate_pdf=False)

        data = {
            'html_content':html_data
        }

        TargetLog.objects.create(target=Target(serializer.data.get('id')), action=7)
        return response(status=True, data=data, status_code=status.HTTP_200_OK, message="HTML generated successfully") 
    
    @swagger_auto_schema(
        tags=['Targets'],
        operation_description= "Delete a host.",
        operation_summary="API to delete a host."
    )
    def destroy(self, request, *args, **kwargs):
        """
        It deletes the record from the database.
        
        :param request: The request object
        :return: The response is being returned.
        """
        self.get_object().soft_delete()
        return response(status=True, data={}, status_code=status.HTTP_200_OK, message="record deleted successfully")

@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "List API.", operation_summary="API to get list of records."))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "Create API.", operation_summary="API to create new record."))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "Retrieve API.", operation_summary="API for retrieve single record by id."))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Tool'], auto_schema=None))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "Partial update API.", operation_summary="API for partial update record."))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "Delete API.", operation_summary="API to delete single record by id."))
class ToolViewSet(viewsets.ModelViewSet):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    permission_classes = [IsAuthenticated, IsAdminUserOrList]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['tool_name', 'tool_cmd', 'subscription__plan_type']
    filterset_fields = ['tool_name', 'tool_cmd', 'subscription__plan_type']
    pagination_class = None

    def list(self, request, *args, **kwargs):
        """
        A function that returns a list of records in response.
        
        :param request: The request object
        :return: The response is being returned.
        """
        serializer = super().list(request, *args, **kwargs)
        return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def create(self, request, *args, **kwargs):
        """
        A function that creates a new record in the database.
        
        :param request: The request object
        :return: The response is being returned.
        """
        self.serializer_class = ToolPayloadSerializer
        serializer = super().create(request, *args, **kwargs)
        return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully added in database.")

    def partial_update(self, request, *args, **kwargs):
        """
        It updates the tool with the given id.
        
        :param request: The request object
        :return: The response is being returned.
        """
        self.serializer_class = ToolPayloadSerializer
        serializer = super().partial_update(request, *args, **kwargs)
        return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully updated in database.")

    def retrieve(self, request, *args, **kwargs):
        """
        It retrieves the data from the database and returns it to the user.
        
        :param request: The request object
        """
        serializer = super().retrieve(request, *args, **kwargs)
        return response(status=True, data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def destroy(self, request, *args, **kwargs):
        """
        It deletes the record from the database.
        
        :param request: The request object
        :return: The response is being returned.
        """
        self.get_object().soft_delete()
        return response(status=True, data={}, status_code=status.HTTP_200_OK, message="record deleted successfully")

@method_decorator(name='get', decorator=swagger_auto_schema(auto_schema=None))
class SendMessageView(generics.GenericAPIView):
    serializer_class = ScannerResponseSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        It takes the id of the target from the query params, gets the target object, serializes it,
        calculates the progress of the scan, adds the progress to the serialized data, sends the data to
        the websocket server and returns a response
        
        :param request: The request object
        :return: The above code is returning the status of the scan.
        """
        start_time = datetime.utcnow()
        params = request.query_params
        while True:
            target = Target.objects.filter(id=params.get('id'))
            serializer = self.serializer_class(target[0])
            diff= (datetime.utcnow() - start_time).total_seconds()
            # api_progress = round(diff*100/((target[0].tool.time_limit+10)), 2)
            api_progress = int(diff*100/((target[0].tool.time_limit+10)))
            record_obj = {**serializer.data, **{'api_progress':api_progress}}
            send(str(record_obj['scan_by']['id']),record_obj)
            if record_obj.get('status') >= 3:
                break
            time.sleep(round(float(settings.WEB_SOCKET_INTERVAL),2))
        return HttpResponse("Done")