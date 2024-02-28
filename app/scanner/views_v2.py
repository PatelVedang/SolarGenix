from django.shortcuts import render
from .models import Target, Tool, TargetLog, Order
from payments.models import PaymentHistory
from user.models import User
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from .tasks import scan, send_message, timeout_handler
from .serializers import *
from rest_framework.response import Response
from rest_framework import viewsets, status, generics, parsers
from rest_framework.decorators import action
from utils.make_response import response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAdminUser
from .permissions import ScannerRetrievePremission, IsAdminUserOrList, IsAuthenticated, UserHasPermission
from user.permissions import CustomIsAdminUser
from django.utils.decorators import method_decorator
# from utils.pdf import PDF
from utils.pdf_final_report import PDF
from django.shortcuts import get_object_or_404
from utils.message import send
from web_socket.serializers import SendMessageSerializer
import time, signal
from datetime import datetime, timedelta, timezone
from django.conf import settings
import logging
logger = logging.getLogger('django')
import json
from django.core.cache import cache
from utils.cache_helper import Cache
from utils.email import send_email
pdf= PDF()
from django.db.models import Q
from dateutil.relativedelta import relativedelta
import textract, traceback
from utils.handlers.octo_pii import Octopii

class Common:

    def update_order_targets(self, order, targets):
        """
        The function updates the status of an order based on the status of its associated targets.
        
        :param order: The "order" parameter is an object representing an order. It likely has attributes
        such as order number, customer information, and order details
        :param targets: The "targets" parameter is a queryset or a list of objects representing the
        targets associated with an order. Each target has a "status" field that indicates its current
        status
        """
        total_targets = targets.count()
        if targets.filter(status__gt=2).count() == total_targets:
            if targets.filter(status=4).count() == total_targets:
                order.update(status=3)
            else:
                order.update(status=2)
        else:
            order.update(status=1)

    def order_update_in_cache(self, order, targets):
        """
        The function `order_update_in_cache` updates the status of an order in the cache based on the
        status of its targets.
        
        :param order: The "order" parameter is a dictionary object that represents an order. It contains
        various attributes such as the order ID, status, and other relevant information
        :param targets: The "targets" parameter is a list of targets that need to be updated in the
        cache. Each target is represented as a dictionary
        :return: the value of the variable "order_scan_finish".
        """
        order_scan_finish = False

        total_targets = len(targets)
        print("\n\n",total_targets, "=>>>>>>>>>>>>total_targets")
        running_targets = Cache.apply_filter(targets,[['status','gt',2]])
        print("\n\n",len(running_targets), "=>>>>>>>>>>>>fail/completed targets")
        complete_targets = Cache.apply_filter(running_targets,[['status','eq',4]])
        print("\n\n",len(complete_targets), "=>>>>>>>>>>>>complete_targets")
        
        if len(running_targets) == total_targets:
            order_scan_finish = True
            if len(complete_targets) == total_targets:
                Order.objects.filter(id=order.get('id')).update(status=3)
                Cache.update(key=f'order_{order.get("id")}',**{'status': 3})
            else:
                Order.objects.filter(id=order.get('id')).update(status=2)
                Cache.update(key=f'order_{order.get("id")}',**{'status': 2})

        return order_scan_finish


    def delete_order_targets_cache(self, order_id):
        """
        The function `delete_order_targets_cache` deletes the cache entries for a specific order and its
        associated targets.
        
        :param order_id: The `order_id` parameter is the unique identifier of the order for which the
        targets cache needs to be deleted
        """
        cache_targets_keys=[]
        order_obj = json.loads(cache.get(f'order_{order_id}','{}'))
        if order_obj:
            targets = order_obj.get('targets',[])
            for target in targets:
                cache_targets_keys.append(f'target_{target["id"]}')
        Cache.delete_many(cache_targets_keys)
        Cache.delete(f'order_{order_id}')
        


@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Targets'], auto_schema=None))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Targets'], auto_schema=None))
class ScanViewSet(viewsets.ModelViewSet, Common):
    queryset = Target.objects.all()
    serializer_class = ScannerSerializer
    permission_classes = [IsAuthenticated, ScannerRetrievePremission, UserHasPermission]
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
        tags=['Targets'],

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
            requested_by_id = request.user.id
            for target_id in targets_id:
                ws_trigger = False
                target_obj = Target.objects.get(id=target_id)
                target_obj.status = 1
                target_obj.save()
                client_id = target_obj.scan_by.id
                tool_time_limit = target_obj.tool.time_limit
                scan.apply_async(args=[], kwargs={'id':target_id, 'time_limit':tool_time_limit, 'token':request.headers.get('Authorization'), 'order_id': target_obj.order_id, 'requested_by_id': requested_by_id, 'client_id': client_id, 'batch_scan': False, 'ws_trigger': ws_trigger}, time_limit=tool_time_limit+int(settings.EXTRA_BG_TASK_TIME), ignore_result=True)
        custom_response = ScannerResponseSerializer(Target.objects.filter(id__in=targets_id), many=True, context={"request": request})
        return response(data=custom_response.data, status_code=status.HTTP_200_OK, message="host successfully added in queue")
        
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
            # if (not request.user.is_staff) and (not request.user.is_superuser):
            if request.user.role_id == 3:
                records = Target.objects.filter(status=0, scan_by=request.user)[:n]
            else:
                records = Target.objects.filter(status=0)[:n]
            records.update(status=1)
            requested_by_id = request.user.id
            for record in records:
                ws_trigger = False
                client_id = record.scan_by.id
                tool_time_limit = record.tool.time_limit
                scan.apply_async(args=[], kwargs={'id':record.id, 'time_limit':tool_time_limit, 'token':request.headers.get('Authorization'), 'order_id': record.order_id, 'requested_by_id': requested_by_id, 'client_id': client_id, 'batch_scan': False, 'ws_trigger': ws_trigger}, time_limit=tool_time_limit+int(settings.EXTRA_BG_TASK_TIME), ignore_result=True)
        custom_response = ScannerResponseSerializer(records, many=True, context={"request": request})
        return response(data=custom_response.data, status_code=status.HTTP_200_OK, message="host successfully added in queue")

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
        custom_response = ScannerResponseSerializer(Target.objects.filter(id__in=record_ids), many=True, context={"request": request})
        return response(data=custom_response.data, status_code=status.HTTP_200_OK, message="host successfully added in database")


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
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

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
        # if (not request.user.is_staff) and (not request.user.is_superuser):
        if request.user.role_id == 3:
            self.queryset = Target.objects.filter(scan_by = request.user.id).order_by('-created_at')
        if request.query_params.get('order'):
            order_id = request.query_params.get('order')
            self.queryset.filter(order_id=order_id)
        self.serializer_class = ScannerResponseSerializer
        data = super().list(request, *args, **kwargs)
        return response(data=data.data, status_code=status.HTTP_200_OK, message="record found successfully")

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
        active_plan = request.user.get_active_plan().exists()
        try:
            pdf_path, pdf_name, file_url = pdf.generate(request.user.role, request.user.id, serializer.data.get('order').get('id'), active_plan, [serializer.data.get('id')])
            
            data = {
                'file_path':file_url
            }
        except Exception as e:
            return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Oops! something went wrong!")
        TargetLog.objects.create(target=Target(serializer.data.get('id')), action=6)
        return response(data=data, status_code=status.HTTP_200_OK, message="PDF generated successfully")
    
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
        active_plan = request.user.get_active_plan().exists()
        try:
            pdf_path, pdf_name, file_url = pdf.generate(request.user.role, request.user.id, serializer.data.get('order').get('id'), active_plan, [serializer.data.get('id')])
            FilePointer = open(pdf_path,"rb")
            
        except Exception as e:
            return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Oops! something went wrong!")
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
        active_plan = request.user.get_active_plan().exists()
        try:
            html_data = pdf.generate(request.user.role, request.user.id, serializer.data.get('order').get('id'), active_plan, [serializer.data.get('id')], generate_pdf=False)
        except Exception as e:
            return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Oops! something went wrong!")

        data = {
            'html_content':html_data
        }

        TargetLog.objects.create(target=Target(serializer.data.get('id')), action=7)
        return response(data=data, status_code=status.HTTP_200_OK, message="HTML generated successfully") 
    
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
        return response(data={}, status_code=status.HTTP_200_OK, message="record deleted successfully")

@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "List API.", operation_summary="API to get list of records."))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Tool'], operation_description= "Create API.", operation_summary="API to create new record.", request_body=ToolPayloadSerializer))
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
        self.serializer_class = ToolPayloadSerializer
        serializer = super().list(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def create(self, request, *args, **kwargs):
        """
        A function that creates a new record in the database.
        
        :param request: The request object
        :return: The response is being returned.
        """
        self.serializer_class = ToolPayloadSerializer
        serializer = super().create(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully added in database.")

    def partial_update(self, request, *args, **kwargs):
        """
        It updates the tool with the given id.
        
        :param request: The request object
        :return: The response is being returned.
        """
        self.serializer_class = ToolPayloadSerializer
        serializer = super().partial_update(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully updated in database.")

    def retrieve(self, request, *args, **kwargs):
        """
        It retrieves the data from the database and returns it to the user.
        
        :param request: The request object
        """
        self.serializer_class = ToolPayloadSerializer
        serializer = super().retrieve(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def destroy(self, request, *args, **kwargs):
        """
        It deletes the record from the database.
        
        :param request: The request object
        :return: The response is being returned.
        """
        self.get_object().soft_delete()
        return response(data={}, status_code=status.HTTP_200_OK, message="record deleted successfully")

@method_decorator(name='get', decorator=swagger_auto_schema(auto_schema=None))
class SendMessageView(generics.GenericAPIView, Common):
    serializer_class = ScannerResponseSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get(self, request, *args, **kwargs):
        """
        It takes the id of the target from the query params, gets the target object, serializes it,
        calculates the progress of the scan, adds the progress to the serialized data, sends the data to
        the websocket server and returns a response
        
        :param request: The request object
        :return: The above code is returning the status of the scan.
        """
        try:
            active_plan = request.user.get_active_plan().exists()
            params = request.query_params
            if params.get('order'):
                targets_start_time = {}
                order_id = params.get('order')
                # order = Order.objects.filter(id=order_id)
                order = Cache.get(f'order_{order_id}')
                while True:
                    order_update = False
                    targets = Cache.get_order_targets(f'order_{order_id}')
                    total_targets = len(targets)
                    print("\n\n",total_targets,"=>>>>>total_targets")
                    # If not found any target relaterd to single order the break while loop
                    if not total_targets:
                        order_percent = 100
                        break   
                    tool_perecent = 100/total_targets
                    response = []
                    order_percent = 0
                    for target_obj in targets:  
                        # Break for loop if target_obj is empty
                        if not target_obj:
                            break
                        # If target in queue
                        if target_obj['status'] == 1:
                            targets_start_time[target_obj['id']] = datetime.utcnow()
                            record_obj = {**target_obj, **{'target_percent':0}}
                            order_percent += int((0*tool_perecent)/100)
                        # If target is running
                        elif (target_obj['status'] == 2) and targets_start_time.get(target_obj['id']):
                            diff= (datetime.utcnow() - targets_start_time[target_obj['id']]).total_seconds()
                            target_percent = int(diff*100/((target_obj['tool']['time_limit']+10)))
                            record_obj = {**target_obj, **{'target_percent':target_percent}}
                            order_percent += int((target_percent*tool_perecent)/100)
                        # if target is just enterd in running stage
                        elif (target_obj['status'] == 2) and not targets_start_time.get(target_obj['id']):
                            targets_start_time[target_obj['id']] = datetime.utcnow()
                            diff= (datetime.utcnow() - targets_start_time[target_obj['id']]).total_seconds()
                            target_percent = int(diff*100/((target_obj['tool']['time_limit']+10)))
                            record_obj = {**target_obj, **{'target_percent':target_percent}}
                            order_percent += int((target_percent*tool_perecent)/100)
                        #  if target is ither fail/complete
                        elif target_obj['status'] > 2:
                            record_obj = {**target_obj, **{'target_percent':100, 'scan_complete': True}}
                            order_percent += int((100*tool_perecent)/100)
                        
                        print(f"Target with id {record_obj['id']} is completed {record_obj['target_percent']}% with status {record_obj['status']}")
                        response.append(record_obj)                    
                    
                    order_update = super().order_update_in_cache(order, response)
                    # If order status is updated
                    if order_update:
                        fresh_order = Cache.get(f'order_{order_id}')
                        order_obj = {**fresh_order, **{'order_percent': order_percent}}
                    else:
                        order_obj = {**order, **{'order_percent': order_percent}}
                    
                    send([str(order['client']['id']), str(request.user.id)],{'order': order_obj, 'targets': response})
                    if order_update:

                        if request.user.subscription.mail_scan_result:
                            # sending mail on scan complete of batch of targets
                            targets_ids = [target.get('id') for target in order['targets']]
                            # active_plan = request.user.get_active_plan().exists()
                            pdf_path, pdf_name, file_url = pdf.generate(request.user.role, request.user.id, order_id, active_plan, targets_ids)
                            user_name = f"{order['client']['first_name']} {order['client']['last_name']}".upper()
                            email_body = settings.SCAN_DELIVERY_MAIL_HTML.get(request.user.language).format(user_name,order['target_ip'],datetime.strptime(order["created_at"],"%Y-%m-%dT%H:%M:%S.%fZ").strftime("%b %d %Y"))
                            send_email(**{
                                'subject':f'Successful Security Scan Results for {order["target_ip"]}',
                                'body':email_body,
                                'sender':settings.BUSINESS_EMAIL,
                                'recipients': list(set([request.user.email, order['client']['email']])),
                                'bcc': settings.SUPPORT_EMAILS,
                                'attachments': [
                                    {
                                        'name': f'scan_result_{datetime.strptime(order["created_at"],"%Y-%m-%dT%H:%M:%S.%fZ").strftime("%b_%d_%Y")}_{order["target_ip"]}.pdf',
                                        'path': pdf_path,
                                        'mime-type': 'application/pdf'
                                    }
                                ],
                                'html_string': email_body
                            })

                        break
                    time.sleep(round(float(settings.WEB_SOCKET_INTERVAL),2))
                # after order is complete we need to remove all the data related to that order from cache
                super().delete_order_targets_cache(order_id)
            else:
                start_time = datetime.utcnow()
                order_id = ''
                while True:
                    target = Cache.get(f'target_{params.get("id")}')
                    print(f"\n\n{target.get('id')} has status {target.get('status')} at {datetime.utcnow()}")
                    print(f"\n\n{target.get('id')} has scan_time {target.get('scan_time')} at {datetime.utcnow()}")
                    if not target:
                        break
                    # serializer = self.serializer_class(target[0], context={"request": request})
                    
                    # Check to see if the target's status is below 3, and if it is, extend the start time to attain a 100% completion rate for the target. 
                    if target.get('status') < 2:
                        start_time = datetime.utcnow()

                    diff= (datetime.utcnow() - start_time).total_seconds()
                    # target_percent = round(diff*100/((target[0].tool.time_limit+10)), 2)
                    target_percent = int(diff*100/((target['tool']['time_limit']+10)))
                    record_obj = {**target, **{'target_percent':target_percent}}
                    send([str(record_obj['scan_by']['id']), str(request.user.id)],record_obj)
                    
                    # Update order status 1 to higher, when last target is update 
                    if record_obj.get('status') >= 3:
                        order_id = record_obj.get('order')
                        order = Cache.get(f'order_{order_id}')
                        targets = Cache.get_order_targets(f'order_{order_id}')
                        order_update = super().order_update_in_cache(order, targets)
                        print(order_update,"=>>>>>>>>>>>>>Order Update")
                        if order_update:
                            order = Cache.get(f'order_{order_id}')
                            order_obj = {**order, **{'order_percent': 100}}
                            record_obj = {**record_obj, **{'target_percent':100}}
                            send([str(order['client']['id']), str(request.user.id)],{'order': order_obj, 'targets': [record_obj]})
                            super().delete_order_targets_cache(order_id)
                        else:
                            # When more than one targets present with status<=2
                            record_obj['target_percent'] = 100
                            send([str(record_obj['scan_by']['id']), str(request.user.id)],record_obj)
                        
                        print(request.user.subscription.mail_scan_result,"=>>>>>>>>Mail Scan  result")
                        if request.user.subscription.mail_scan_result:
                            # sending mail on scan complete of single target
                            # active_plan = request.user.get_active_plan().exists()
                            pdf_path, pdf_name, file_url = pdf.generate(request.user.role, request.user.id, order_id, active_plan, [record_obj["id"]])
                            user_name = f"{order['client']['first_name']} {order['client']['last_name']}".upper()
                            email_body = settings.SCAN_DELIVERY_MAIL_HTML.get(request.user.language).format(user_name,record_obj["ip"],datetime.strptime(record_obj["created_at"],"%Y-%m-%dT%H:%M:%S.%fZ").strftime("%b_%d_%Y"))
                            send_email(**{
                                'subject':f'Successful Security Scan Results for {record_obj["ip"]}',
                                'body':email_body,
                                'sender':settings.BUSINESS_EMAIL,
                                'recipients': list(set([request.user.email, order['client']['email']])),
                                'bcc': settings.SUPPORT_EMAILS,
                                'attachments': [
                                    {
                                        'name': f'scan_result_{datetime.strptime(record_obj["created_at"],"%Y-%m-%dT%H:%M:%S.%fZ").strftime("%b_%d_%Y")}_{record_obj["ip"]}.pdf',
                                        'path': pdf_path,
                                        'mime-type': 'application/pdf'
                                    }
                                ],
                                'html_string': email_body
                            })
                        break
                    time.sleep(round(float(settings.WEB_SOCKET_INTERVAL),2))


        except Exception as e:
            print("Error=>", e)
            import traceback
            traceback.print_exc()
        return HttpResponse("Done")


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Orders'], operation_description= "List API.", operation_summary="API to get list of records."))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Orders'], operation_description= "Create API.", operation_summary="API to create new record."))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Orders'], operation_description= "Retrieve API.", operation_summary="API for retrieve single record by id."))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Orders'], auto_schema=None))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Orders'], operation_description= "Partial update API.", operation_summary="API for partial update record.", request_body=OrderUpdateSerailizer))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Orders'], operation_description= "Delete API.", operation_summary="API to delete single record by id."))
class OrderViewSet(viewsets.ModelViewSet, Common):
    queryset = Order.objects.all()
    serializer_class = OrderSerailizer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['client_id', 'target_ip']
    search_fields = ['target_ip', 'client__first_name', 'client__last_name', 'updated_at']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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
            today = datetime.utcnow()
            current_sub = request.user.get_active_plan()
            if request.user.role.id!=1:
                # If user have any running subscription
                if current_sub.exists():
                    # Getting IP limit
                    ip_limit = current_sub[0].ip_limit
                    # Getting plan type (1, 'Recurring') (2, 'One Time')
                    plan_type = current_sub[0].price_type
                    if plan_type in [1,2]:
                        # If plan is recurring
                        orders = Order.default.filter(client_id=request.user.id, created_at__gte=current_sub[0].current_period_start, created_at__lte=current_sub[0].current_period_end)
                        if orders.count()>=ip_limit:
                            return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="You have reached your IP limit. Please upgrade your account!!")
                        
                        # one_month_ago = datetime.utcfromtimestamp(int((today - relativedelta(months=1)).timestamp())).replace(tzinfo=timezone.utc)
                        # if one_month_ago < current_sub[0].current_period_start:
                        #     start = current_sub[0].current_period_start
                        #     end = (current_sub[0].current_period_end if plan_type==1 else (today + relativedelta(months=1)))
                        # else:
                        #     start = one_month_ago
                        #     end = today
                        
                        # # interval_orders = orders.filter(created_at__gte=start, created_at__lte=end)

                        # # if interval_orders.count()>=1:
                        # #     return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Oops! It seems you've hit the limit for IP usage this month.")
                        
                        # same_ip_orders = orders.filter(created_at__gte=start, created_at__lte=end,target_ip=target_ip)

                        # if same_ip_orders.count()>=1:
                        #     return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Oops! It seems like this IP address has already been scanned this month.")

                    elif plan_type == 3:
                        # If plan is only for one time
                        orders = Order.default.filter(client_id=request.user.id, created_at__gte=current_sub[0].current_period_start, created_at__lte=today)

                        if orders.count()>=ip_limit:
                            return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="You have reached your IP limit. Please upgrade your account!!")

                        # same_ip_orders = orders.filter(target_ip=target_ip)

                        # if same_ip_orders.count()>=1:
                        #     return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Oops! It seems like you've already scanned this domain once. So please try another domain!")
                else:
                    # If user has free subscription
                    ip_limit = 1
                    start_date = today - timedelta(days=15)
                    
                    orders = Order.default.filter(client_id=request.user.id, created_at__gte=start_date, created_at__lte=today)
                    if orders.count()>=ip_limit:
                        return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="You have reached your IP limit. Please upgrade your account!!")
                    
                    
            order = Order.objects.create(client_id=request.user.id, subscrib_id=request.user.subscription_id, target_ip=target_ip)
            
            if 'files' in request.FILES:
                order.company_logo = request.FILES['files']
                order.company_name = serializer.data.get('company_name','')
                order.company_address = serializer.data.get('company_address','')
                order.is_client = serializer.data.get('is_client',False)
                order.client_name = serializer.data.get('client_name','')
                order.save()

            custom_response = OrderResponseSerailizer(order, context={"request": request})
            return response(data=custom_response.data, status_code=status.HTTP_200_OK, message="order successfully added in database")
    
    def partial_update(self, request, *args, **kwargs):
        if request.user.role.id==4:
            self.serializer_class = OrderUpdateSerailizer
            request.data['company_logo'] = request.FILES['files']
            serializer = super().partial_update(request, *args, **kwargs)
            order = Order.objects.get(id=kwargs.get('pk'))
            custom_response = OrderResponseSerailizer(order, context={"request": request})
            return response(data=custom_response.data, status_code=status.HTTP_200_OK, message="record successfully updated in database.")
        else:
            return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Oops! something went wrong!")
        
    def list(self, request, *args, **kwargs):
        """
        A function that returns list of orders.
        
        :param request: The request object
        :return: The response is being returned.
        """
        # if not request.user.is_superuser:
        if request.user.role_id!=1:
            self.queryset = Order.objects.filter(client_id = request.user.id)
        self.serializer_class = OrderResponseSerailizer
        data = super().list(request, *args, **kwargs)
        return response(data=data.data, status_code=status.HTTP_200_OK, message="record found successfully")
    
    def retrieve(self, request, *args, **kwargs):
        """
        It overrides the default retrieve function of the viewset and returns a custom response
        
        :param request: The request object
        :return: The response is being returned.
        """
        self.serializer_class = OrderResponseSerailizer
        data = super().retrieve(request, *args, **kwargs)
        return response(data=data.data, status_code=status.HTTP_200_OK, message="record found successfully")
    
    def destroy(self, request, *args, **kwargs):
        """
        It deletes the record from the database.
        
        :param request: The request object
        :return: The response is being returned.
        """
        order = self.get_object()
        Target.objects.filter(order=order).update(is_deleted=True)
        self.get_object().soft_delete()
        return response(data={}, status_code=status.HTTP_200_OK, message="record deleted successfully")
    
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
                requested_by_id = request.user.id
                targets = Target.objects.filter(order_id=order_id, status__lte=2)
                targets.update(status=1)
                super().update_order_targets(order, targets)
                for index in range(len(targets)):
                # for target in targets:
                    ws_trigger = False
                    if index == 0:
                        ws_trigger = True
                    client_id = targets[index].scan_by.id
                    
                    scan.apply_async(args=[], kwargs={'id':targets[index].id, 'time_limit':targets[index].tool.id, 'token':request.headers.get('Authorization'), 'order_id': order_id, 'requested_by_id': requested_by_id, 'client_id': client_id, 'batch_scan': True, 'ws_trigger': ws_trigger}, time_limit=targets[index].tool.time_limit + int(settings.EXTRA_BG_TASK_TIME), ignore_result=True)
        custom_response = OrderResponseSerailizer(Order.objects.filter(id__in=orders_id), many=True, context={"request": request})
        return response(data=custom_response.data, status_code=status.HTTP_200_OK, message="Your target has been added to the scan queue.")

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
        targets = [target.get('id') for target in (list(Target.objects.filter(order_id= serializer.data.get('id')).values('id')))]
        active_plan = request.user.get_active_plan().exists()
        try:
            pdf_path, pdf_name, file_url = pdf.generate(request.user.role, request.user.id, serializer.data.get('id'), active_plan, targets_ids=targets, generate_order_pdf=True)
        except Exception as e:
            return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Oops! something went wrong!")
        data = {
            'file_path':file_url
        }
        return response(data=data, status_code=status.HTTP_200_OK, message="PDF generated successfully")


@method_decorator(name='list', decorator=swagger_auto_schema(tags=['Subscriptions'], operation_description= "List API.", operation_summary="API to get list of records."))
@method_decorator(name='create', decorator=swagger_auto_schema(tags=['Subscriptions'], operation_description= "Create API.", operation_summary="API to create new record."))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(tags=['Subscriptions'], operation_description= "Retrieve API.", operation_summary="API for retrieve single record by id."))
@method_decorator(name='update', decorator=swagger_auto_schema(tags=['Subscriptions'], auto_schema=None))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(tags=['Subscriptions'], operation_description= "Partial update API.", operation_summary="API for partial update record."))
@method_decorator(name='destroy', decorator=swagger_auto_schema(tags=['Subscriptions'], operation_description= "Delete API.", operation_summary="API to delete single record by id."))
class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [CustomIsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['plan_type']
    filterset_fields = ['plan_type']
    ordering_fields = ['plan_type']

    @swagger_auto_schema(
        method = 'get',
        operation_description= "Get all the subscriptions without pagination",
        operation_summary="API to get all subscriptions.",
        request_body=None,
        tags=['Subscriptions']

    )
    @action(methods=['GET'], detail=False, url_path="all")
    def get_all(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def list(self, request, *args, **kwargs):
        serializer = super().list(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")

    def retrieve(self, request, *args, **kwargs):
        serializer = super().retrieve(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record found successfully")
    
    def create(self, request, *args, **kwargs):
        serializer = super().create(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully added in database.")
    
    def partial_update(self, request, *args, **kwargs):
        serializer = super().partial_update(request, *args, **kwargs)
        return response(data=serializer.data, status_code=status.HTTP_200_OK, message="record successfully updated in database.")
    
    def destroy(self, request, *args, **kwargs):
        self.get_object().soft_delete()
        return response(data={}, status_code=status.HTTP_200_OK, message="record deleted successfully")

import threading

@method_decorator(name='post', decorator=swagger_auto_schema(tags=['Octopii'], operation_description= "Scan single file API.", operation_summary="API to scan uploaded file with octpii."))
class OctopiiView(generics.CreateAPIView):
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.FileUploadParser)
    serializer_class = OctopiiSingleFileSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, *args, **kwargs):
        """
        This Python function handles file uploads, processes the file using Octopii, and returns the
        result or appropriate error messages.
        
        :param request: The `request` parameter in the `post` method is typically an object that
        contains information about the HTTP request that triggered the view, including data sent in the
        request, such as files uploaded through a form. In this specific code snippet, the `request`
        object is used to retrieve the uploaded file
        :return: The code is returning a response with data, status code, and a message. The data being
        returned is either the result of processing the uploaded file using the Octopii class or an
        empty dictionary if an exception occurs. The status code returned is either 200 (OK) if the
        processing is successful or 500 (Internal Server Error) if an exception occurs. The message
        returned is either "success
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                file = serializer.validated_data['file']
                oct = Octopii(file)
                result = oct.main()
            except Exception as e:
                return response(data={}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e))
        
        return response(data=result, status_code=status.HTTP_200_OK, message="file scan completed")
    