from django.shortcuts import render
from .models import Target, Tool, TargetLog, Order
from user.models import User
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .tasks import scan
from .serializers import *
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

class Common:

    def update_order_targets(self, order, targets):
        total_targets = targets.count()
        if targets.filter(status__gt=2).count() == total_targets:
            if targets.filter(status=4).count() == total_targets:
                order.update(status=3)
            else:
                order.update(status=2)
        else:
            order.update(status=1)


@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Targets'], auto_schema=None))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Targets'], auto_schema=None))
class ScanViewSet(viewsets.ModelViewSet, Common):
    queryset = Target.objects.all()
    serializer_class = ScannerSerializer
    permission_classes = [IsAuthenticated, MachineRetrievePremission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['ip', 'scan_by__first_name', 'scan_by__last_name', 'tool__tool_name', 'updated_at']
    filterset_fields = ['id', 'ip', 'status', 'tool', 'order']
    ordering_fields = ['tool__tool_name', 'ip', 'id', 'created_at', 'updated_at', 'status']
    # filterset_class = MetricFilter

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
                target_obj.status = 1
                target_obj.save()
                tool_time_limit = target_obj.tool.time_limit
                scan.apply_async(args=[], kwargs={'id':target_id, 'time_limit':tool_time_limit, 'token':request.headers.get('Authorization'), 'order_id': target_obj.order_id, 'batch_scan': False}, time_limit=tool_time_limit+10, ignore_result=True)
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
            records.update(status=1)
            for record in records:
                tool_time_limit = record.tool.time_limit
                scan.apply_async(args=[], kwargs={'id':record.id, 'time_limit':tool_time_limit, 'token':request.headers.get('Authorization'), 'order_id': record.order_id, 'batch_scan': False}, time_limit=tool_time_limit+10, ignore_result=True)
        custom_response = ScannerResponseSerializer(records, many=True)
        return response(status=True, data=custom_response.data, status_code=status.HTTP_200_OK, message="host successfully added in queue")

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
            # tools = serializer.data.get('tools_id')
            scan_by = serializer.data.get('scan_by')
            if isinstance(ip_addresses, str):
                ip_addresses = [ip_addresses]
            # if isinstance(tools, int):
            #     tools = [tools]
            record_ids = []
            
            # in future we will update below filter condition
            tools = Tool.objects.filter(subscription_id=1)
            
            for ip in ip_addresses:
                # in future we will update below filter condition
                order = Order.objects.create(client_id=request.user.id, subscrib_id=1, target_ip=ip)
                for tool in tools:
                    obj = Target.objects.create(ip=ip, scan_by=request.user,tool=tool, order=order)
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
        if request.query_params.get('order'):
            order_id = request.query_params.get('order')
            self.queryset.filter(order_id=order_id)
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
        pdf_path, pdf_name, file_url = pdf.generate(request.user.id, serializer.data.get('order'), [serializer.data.get('id')])
        
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
        pdf_path, pdf_name, file_url = pdf.generate(request.user.id, serializer.data.get('order'), [serializer.data.get('id')])
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
        
        html_data = pdf.generate(request.user.id, serializer.data.get('order'), [serializer.data.get('id')], generate_pdf=False)

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
class ToolViewSet(viewsets.ModelViewSet, Common):
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
class SendMessageView(generics.GenericAPIView, Common):
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
        params = request.query_params
        if params.get('order'):
            targets_start_time = {}
            order_id = params.get('order')
            order = Order.objects.filter(id=order_id)
            # order.update(status=1)
            while True:
                targets = Target.objects.filter(order_id=order_id)
                total_targets = targets.count()
                tool_perecent = 100/total_targets
                response = []
                order_percent = 0
                for target in targets:
                    serializer = self.serializer_class(target)
                    if (target.status < 3 and target.status > 0) and targets_start_time.get(target.id):
                        diff= (datetime.utcnow() - targets_start_time[target.id]).total_seconds()
                        target_percent = int(diff*100/((target.tool.time_limit+10)))
                        record_obj = {**serializer.data, **{'target_percent':target_percent}}
                        order_percent += int((target_percent*tool_perecent)/100)
                        response.append(record_obj)
                    elif (target.status < 3 and target.status > 0) and not targets_start_time.get(target.id):
                        targets_start_time[target.id] = datetime.utcnow()
                        diff= (datetime.utcnow() - targets_start_time[target.id]).total_seconds()
                        target_percent = int(diff*100/((target.tool.time_limit+10)))
                        record_obj = {**serializer.data, **{'target_percent':target_percent}}
                        order_percent += int((target_percent*tool_perecent)/100)
                        response.append(record_obj)
                    elif target.status > 2:
                        record_obj = {**serializer.data, **{'target_percent':100, 'scan_complete': True}}
                        order_percent += int((100*tool_perecent)/100)
                        response.append(record_obj)
                    elif target.status == 0:
                        record_obj = {**serializer.data, **{'target_percent':0}}
                        order_percent += int((0*tool_perecent)/100)
                        response.append(record_obj)

                    super().update_order_targets(order, targets)
                    
                serializer = OrderWithoutTargetsResponseSerailizer(order, many=True)
                order_obj = {**serializer.data[0], **{'order_percent': order_percent}}
                send(str(order[0].client_id),{'order': order_obj, 'targets': response})
                if order[0].status >= 2:
                    break
                time.sleep(round(float(settings.WEB_SOCKET_INTERVAL),2))
        else:
            start_time = datetime.utcnow()
            while True:
                target = Target.objects.filter(id=params.get('id'))
                serializer = self.serializer_class(target[0])
                diff= (datetime.utcnow() - start_time).total_seconds()
                # target_percent = round(diff*100/((target[0].tool.time_limit+10)), 2)
                target_percent = int(diff*100/((target[0].tool.time_limit+10)))
                record_obj = {**serializer.data, **{'target_percent':target_percent}}
                send(str(record_obj['scan_by']['id']),record_obj)
                response = []
                if record_obj.get('status') >= 3:
                    order_id=target[0].order_id
                    targets = Target.objects.filter(order_id=order_id)
                    order = Order.objects.filter(id=order_id)
                    print(targets.filter(status__gt=2).count() == targets.count(),"=>>>")
                    if targets.filter(status__gt=2).count() == targets.count():
                        if targets.filter(status=4).count() == targets.count():
                            order.update(status=3)
                        else:
                            order.update(status=2)
                        targets = self.serializer_class(targets, many=True)
                        for record in targets.data:
                            if record['id'] == target[0].id:
                                obj = {**record, **{'target_percent':100}}
                            else:
                                obj = {**record, **{'target_percent':100, 'scan_complete': True}}
                            response.append(obj)
                        serializer = OrderWithoutTargetsResponseSerailizer(order, many=True)
                        order_obj = {**serializer.data[0], **{'order_percent': 100}}
                        send(str(order[0].client_id),{'order': order_obj, 'targets': response})
                    else:
                        record_obj['target_percent'] = 100
                        send(str(record_obj['scan_by']['id']),record_obj)
                    break
                time.sleep(round(float(settings.WEB_SOCKET_INTERVAL),2))
        return HttpResponse("Done")


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Orders'], operation_description= "List API.", operation_summary="API to get list of records."))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Orders'], operation_description= "Create API.", operation_summary="API to create new record."))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Orders'], operation_description= "Retrieve API.", operation_summary="API for retrieve single record by id."))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Orders'], auto_schema=None))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Orders'], operation_description= "Partial update API.", operation_summary="API for partial update record."))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Orders'], operation_description= "Delete API.", operation_summary="API to delete single record by id."))
class OrderViewSet(viewsets.ModelViewSet, Common):
    queryset = Order.objects.all()
    serializer_class = OrderSerailizer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['client_id', 'target_ip']
    search_fields = ['target_ip', 'client__first_name', 'client__last_name', 'updated_at']

    def create(self, request, *args, **kwargs):
        """
        I'm creating an order and then I'm creating a target for each tool that is associated with the
        subscription that the order is associated with
        
        :param request: The request object
        """
        self.serializer_class = OrderSerailizer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            target_ip= serializer.data.get('target_ip')
            order = Order.objects.create(client_id=request.user.id, subscrib_id=1, target_ip=target_ip)
            tools = Tool.objects.filter(subscription_id=1)
            targets= []
            for tool in tools:
                targets.append(Target(ip=target_ip, raw_result="", tool=tool, order=order, scan_by = request.user))
            Target.objects.bulk_create(targets)
            custom_response = OrderResponseSerailizer(order)
            return response(status=True, data=custom_response.data, status_code=status.HTTP_200_OK, message="order successfully added in database")
        
    def list(self, request, *args, **kwargs):
        """
        A function that returns list of orders.
        
        :param request: The request object
        :return: The response is being returned.
        """
        if (not request.user.is_staff) and (not request.user.is_superuser):
            self.queryset = Order.objects.filter(client_id = request.user.id)
        self.serializer_class = OrderResponseSerailizer
        data = super().list(request, *args, **kwargs)
        return response(status=True, data=data.data, status_code=status.HTTP_200_OK, message="record found successfully")
    
    def retrieve(self, request, *args, **kwargs):
        """
        It overrides the default retrieve function of the viewset and returns a custom response
        
        :param request: The request object
        :return: The response is being returned.
        """
        self.serializer_class = OrderResponseSerailizer
        data = super().list(request, *args, **kwargs)
        return response(status=True, data=data.data, status_code=status.HTTP_200_OK, message="record found successfully")
    
    def destroy(self, request, *args, **kwargs):
        """
        It deletes the record from the database.
        
        :param request: The request object
        :return: The response is being returned.
        """
        order = self.get_object()
        Target.objects.filter(order=order).update(is_deleted=True)
        self.get_object().soft_delete()
        return response(status=True, data={}, status_code=status.HTTP_200_OK, message="record deleted successfully")
    
    @swagger_auto_schema(
        method = 'post',
        request_body=AddInQueueByOrderIdsSerializer,
        operation_description= "Set targets in queue by order id.",
        operation_summary="API to add targets in queue for scanning by ids using order id.",
        tags=['Orders']

    )
    @action(methods=['POST'], detail=False, url_path="addByIds")
    def scan_by_ids(self, request, *args, **kwargs):
        """
        It takes a list of order ids, and for each order id, it takes all the targets associated with
        that order id, and adds them to the queue
        
        :param request: The request object
        """
        self.serializer_class = AddInQueueByOrderIdsSerializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            orders_id = serializer.data.get('orders_id')
            for order_id in orders_id:
                order = Order.objects.filter(id=order_id)
                targets = Target.objects.filter(order_id=order_id, status__lte=2)
                targets.update(status=1)
                super().update_order_targets(order, targets)
                # if order[0].status == 0:
                for target in targets:
                    scan.apply_async(args=[], kwargs={'id':target.id, 'time_limit':target.tool.id, 'token':request.headers.get('Authorization'), 'order_id': order_id, 'batch_scan': True}, time_limit=target.tool.time_limit +10, ignore_result=True)
        custom_response = OrderResponseSerailizer(Order.objects.filter(id__in=orders_id), many=True)
        return response(status=True, data=custom_response.data, status_code=status.HTTP_200_OK, message="targets of order is successfully added in queue")

    @swagger_auto_schema(
        method = 'get',
        operation_description= "Generate pdf from a scan result. And provide url of pdf as aresponse.",
        operation_summary="API to generate pdf url.",
        tags=['Orders'],
        request_body=None

    )
    @action(methods=['GET'], detail=True, url_path="generateReport")
    def generate_batch_report(self, request, *args, **kwargs):
        """
        It takes the id of the user and the batch id to generates a pdf file url
        
        :param request: The request object
        :return: A PDF file url
        """
        self.serializer_class = OrderResponseSerailizer
        serializer = super().retrieve(request, *args, **kwargs)
        pdf= PDF()
        targets = [target.get('id') for target in (list(Target.objects.filter(order_id= serializer.data.get('id')).values('id')))]
        pdf_path, pdf_name, file_url = pdf.generate(request.user.id, serializer.data.get('id'), targets_ids=targets, generate_order_pdf=True)
        data = {
            'file_path':file_url
        }
        return response(status=True, data=data, status_code=status.HTTP_200_OK, message="PDF generated successfully")
    