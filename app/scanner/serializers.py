from rest_framework import serializers
from .models import Target, Tool, Order, Subscription
from user.models import User
# from django.core.validators import validate_ipv4_address
import logging
logger = logging.getLogger('django')
import json
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import socket
import ipaddress
from tldextract import extract
from django.conf import settings

   
def validate_ipv4_address(value):
    """
    It takes a string, tries to resolve it as a domain name, and if it can't, it tries to validate it as
    an IPv4 address
    
    :param value: The value that is being validated
    """

    try:
        value = ".".join(list(extract(value))).strip(".")
        value = socket.gethostbyname(value)
    except Exception as e:
        message = str(e).split("] ")[1] if len(str(e).split("] "))>1 else "Invalid domain name"
        raise ValidationError(
            
            _("Name or service not known"), code="invalid", params={"value": value}
        )
    
    try:
        ipaddress.IPv4Address(value)
    except ValueError:
        raise ValidationError(
            _("Enter a valid IPv4 address."), code="invalid", params={"value": value}
        )
    else:
        # Leading zeros are forbidden to avoid ambiguity with the octal
        # notation. This restriction is included in Python 3.9.5+.
        # TODO: Remove when dropping support for PY39.
        if any(octet != "0" and octet[0] == "0" for octet in value.split(".")):
            raise ValidationError(
                _("Enter a valid IPv4 address."),
                code="invalid",
                params={"value": value},
        )

# This class is a serializer for the Target model. It has a custom validation method that checks if
# the tools_id field is a list of integers that correspond to existing Tool objects
class ScannerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    ip = serializers.ListField(child=serializers.CharField(validators=[validate_ipv4_address]))
    tools_id = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    
    class Meta:
        model = Target
        fields = ['ip','id','tools_id']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        tools_id = attrs['tools_id']
        for tool_id in tools_id:
            if not Tool.objects.filter(id=tool_id).exists():
                raise serializers.DjangoValidationError(f"Tool does not exist with id {tool_id}")
        return super().validate(attrs)


# The ToolPayloadSerializer class is a subclass of the ModelSerializer class. It has a Meta class that
# specifies the model to be serialized and the fields to be serialized. It also has a validate method
# that logs the serialized data
class ToolPayloadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Tool
        exlude = ['is_deleted']
        fields = ['id','tool_name','tool_cmd', 'time_limit']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        return super().validate(attrs)


# This serializer consider as a response serializer for Tool model. 
class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'is_deleted', 'tool_name', 'tool_cmd', 'time_limit']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        return super().validate(attrs)

# The ScannerResponseSerializer class is a subclass of the ModelSerializer class. It has a Meta class
# that specifies the model to be used and the fields to be serialized. The to_representation method is
# overridden to add the tool name to the serialized data
class ScannerResponseSerializer(serializers.ModelSerializer):
    tool =  ToolPayloadSerializer()

    class Meta:
        model = Target
        exclude = ['compose_result']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        requested_user = self.context['request'].user
        if not requested_user.role.tool_access:
            data['tool']= instance.tool.id
            data['raw_result'] = ""
        
        data['scan_by']= {
            "id": instance.scan_by.id,
            "email": instance.scan_by.email,
            "first_name": instance.scan_by.first_name,
            "last_name": instance.scan_by.last_name,
            "is_staff": instance.scan_by.is_staff,
            "is_superuser": instance.scan_by.is_superuser,
            "role_id": instance.scan_by.role_id,
            "subscription_id": instance.scan_by.subscription_id
        }
        data['request_by']= {
            "id": requested_user.id,
            "email": requested_user.email,
            "first_name": requested_user.first_name,
            "last_name": requested_user.last_name,
            "is_staff": requested_user.is_staff,
            "is_superuser": requested_user.is_superuser,
            "role": {
                'id': requested_user.role.id,
                'name': requested_user.role.name,
                'tool_access': requested_user.role.tool_access,
                'target_access':requested_user.role.target_access,
                'client_name_access':requested_user.role.client_name_access,
                'scan_result_access':requested_user.role.scan_result_access,
                'cover_content_access':requested_user.role.cover_content_access
            },
            "subscription_id": requested_user.subscription_id
        }
        return data
    
    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        return super().validate(attrs)


# The `OrderSerializer` class is a subclass of `serializers.ModelSerializer` and it has a `target_ip`
# field that is a `serializers.CharField` with a `validate_ipv4_address` validator
class OrderSerailizer(serializers.ModelSerializer):
    target_ip = serializers.CharField(validators=[validate_ipv4_address])
    company_name = serializers.CharField(required=False, max_length=100)
    company_address = serializers.CharField(required=False)
    is_client = serializers.BooleanField(required=False)
    client_name = serializers.CharField(required=False, max_length=100)

    class Meta:
        model = Order
        fields = ['target_ip', 'company_name', 'company_address', 'is_client', 'client_name']

    
    def save(self, **kwargs):
        return super().save(**kwargs)


# The `OrderSerializer` class is a subclass of `serializers.ModelSerializer` and it has a `target_ip`
# field that is a `serializers.CharField` with a `validate_ipv4_address` validator
class OrderUpdateSerailizer(serializers.ModelSerializer):
    company_name = serializers.CharField(required=False, max_length=100)
    company_address = serializers.CharField(required=False)
    is_client = serializers.BooleanField(required=False)
    client_name = serializers.CharField(required=False, max_length=100)
    company_logo = serializers.ImageField()

    class Meta:
        model = Order
        fields = ['company_name', 'company_address', 'is_client', 'client_name', 'company_logo']

    
    def save(self, **kwargs):
        return super().save(**kwargs)


# The OrderResponseSerializer class is a subclass of the ModelSerializer class. It has a Meta class
# that specifies the model to be serialized and the fields to be serialized. It also has a
# to_representation method that overrides the to_representation method of the ModelSerializer class.
# The to_representation method is used to add the client field to the serialized data
class OrderResponseSerailizer(serializers.ModelSerializer):
    targets = ScannerResponseSerializer(many=True, read_only= True)


    class Meta:
        model = Order
        fields = "__all__"

    def to_representation(self, instance):
        requested_user = self.context['request'].user
        data = super().to_representation(instance)

        data['client']= {
            "id": instance.client.id,
            "email": instance.client.email,
            "first_name": instance.client.first_name,
            "last_name": instance.client.last_name,
            "is_staff": instance.client.is_staff,
            "is_superuser": instance.client.is_superuser,
            "role_id": instance.client.role_id,
            "subscription_id": instance.client.subscription_id
        }
        data['request_by']= {
            "id": requested_user.id,
            "email": requested_user.email,
            "first_name": requested_user.first_name,
            "last_name": requested_user.last_name,
            "is_staff": requested_user.is_staff,
            "is_superuser": requested_user.is_superuser,
            "role": {
                'id': requested_user.role.id,
                'name': requested_user.role.name,
                'tool_access': requested_user.role.tool_access,
                'target_access':requested_user.role.target_access,
                'client_name_access':requested_user.role.client_name_access,
                'scan_result_access':requested_user.role.scan_result_access,
                'cover_content_access':requested_user.role.cover_content_access
            },
            "subscription_id": requested_user.subscription_id
        }
        data['company_logo'] = (f'{settings.PDF_DOWNLOAD_ORIGIN}/media/{str(instance.company_logo)}' if instance.company_logo else "")
        return data


# This class is similar to OrderResponseSerailizer, but only the difference is here we are not providing
# the targets in serialize data 
class OrderWithoutTargetsResponseSerailizer(serializers.ModelSerializer):
    
    class Meta:
        model = Order
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        requested_user = self.context['request'].user
        data['client']= {
            "id": instance.client.id,
            "email": instance.client.email,
            "first_name": instance.client.first_name,
            "last_name": instance.client.last_name,
            "is_staff": instance.client.is_staff,
            "is_superuser": instance.client.is_superuser,
            "role_id": instance.client.role_id,
            "subscription_id": instance.client.subscription_id
        }
        data['request_by']= {
            "id": requested_user.id,
            "email": requested_user.email,
            "first_name": requested_user.first_name,
            "last_name": requested_user.last_name,
            "is_staff": requested_user.is_staff,
            "is_superuser": requested_user.is_superuser,
            "role": {
                'id': requested_user.role.id,
                'name': requested_user.role.name,
                'tool_access': requested_user.role.tool_access,
                'target_access':requested_user.role.target_access,
                'client_name_access':requested_user.role.client_name_access,
                'scan_result_access':requested_user.role.scan_result_access,
                'cover_content_access':requested_user.role.cover_content_access
            },
            "subscription_id": requested_user.subscription_id
        }
        return data



# This class is a serializer that takes a list of target ids and validates that each target id exists
# in the database
class AddInQueueByIdsSerializer(serializers.ModelSerializer):
    targets_id = serializers.ListField(child = serializers.IntegerField(), allow_empty=False)
    class Meta:
        model = Target
        fields = ['targets_id']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        targets_id = attrs['targets_id']
        for target_id in targets_id:
            if not Target.objects.filter(id=target_id).exists():
                raise serializers.DjangoValidationError(f"Target does not exist with id {target_id}")
        return super().validate(attrs)


# It's a serializer that takes a count of how many numbers to add to the queue, and then adds that
# many numbers to the queue
class AddInQueueByNumbersSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()
    class Meta:
        model = Target
        fields = ['count']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        return super().validate(attrs)


    

# This class is a serializer for the `Order` model. It has a field called `orders_id` which is a list
# of integers. The `validate` method checks if the order exists in the database
class AddInQueueByOrderIdsSerializer(serializers.ModelSerializer):
    orders_id = serializers.ListField(child = serializers.IntegerField(), allow_empty=False)
    class Meta:
        model = Order
        fields = ['orders_id']

    def validate(self, attrs):
        logger.info(f'serialize_data: {json.dumps(attrs)}')
        orders_id = attrs['orders_id']
        for order_id in orders_id:
            if not Order.objects.filter(id=order_id).exists():
                raise serializers.DjangoValidationError(f"Order does not exist with id {order_id}")
        return super().validate(attrs)


# The class `WithoutRequestUserTargetSerializer` is a serializer that excludes the `compose_result`
# field from the `Target` model and adds additional representation data based on the context.
# This serializer is provide targets without providing requested user from request
class WithoutRequestUserTargetSerializer(serializers.ModelSerializer):
    tool =  ToolPayloadSerializer()

    class Meta:
        model = Target
        exclude = ['compose_result']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        requested_by_id = self.context['requested_by_id']
        requested_by = User.objects.get(id=requested_by_id)
        # if not requested_by.role.tool_access:
        #     data['tool']= instance.tool.id
        #     data['raw_result'] = ""
        
        data['scan_by']= {
            "id": instance.scan_by.id,
            "email": instance.scan_by.email,
            "first_name": instance.scan_by.first_name,
            "last_name": instance.scan_by.last_name,
            "is_staff": instance.scan_by.is_staff,
            "is_superuser": instance.scan_by.is_superuser,
            "role_id": instance.scan_by.role_id,
            "subscription_id": instance.scan_by.subscription_id
        }
        data['request_by']= {
            "id": requested_by.id,
            "email": requested_by.email,
            "first_name": requested_by.first_name,
            "last_name": requested_by.last_name,
            "is_staff": requested_by.is_staff,
            "is_superuser": requested_by.is_superuser,
            "role": {
                'id': requested_by.role.id,
                'name': requested_by.role.name,
                'tool_access': requested_by.role.tool_access,
                'target_access':requested_by.role.target_access,
                'client_name_access':requested_by.role.client_name_access,
                'scan_result_access':requested_by.role.scan_result_access,
                'cover_content_access':requested_by.role.cover_content_access
            },
            "subscription_id": requested_by.subscription_id
        }
        return data

# The class `ScannerDummyResponseSerializer` is a serializer for the `Target` model that only includes
# the `id` field.
class ScannerDummyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ['id']


# The class `WithoutRequestUserOrderSerializer` is a serializer class in Python that serializes an
# `Order` model and includes additional information about the client and the user who requested the
# order.
# This serializer is provide orders without providing requested user from request
class WithoutRequestUserOrderSerializer(serializers.ModelSerializer):
    targets = ScannerDummyResponseSerializer(many=True, read_only= True)
    class Meta:
        model = Order
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        requested_by_id = self.context['requested_by_id']
        requested_by = User.objects.get(id=requested_by_id)
        data['client']= {
            "id": instance.client.id,
            "email": instance.client.email,
            "first_name": instance.client.first_name,
            "last_name": instance.client.last_name,
            "is_staff": instance.client.is_staff,
            "is_superuser": instance.client.is_superuser,
            "role_id": instance.client.role_id,
            "subscription_id": instance.client.subscription_id
        }
        data['request_by']= {
            "id": requested_by.id,
            "email": requested_by.email,
            "first_name": requested_by.first_name,
            "last_name": requested_by.last_name,
            "is_staff": requested_by.is_staff,
            "is_superuser": requested_by.is_superuser,
            "role": {
                'id': requested_by.role.id,
                'name': requested_by.role.name,
                'tool_access': requested_by.role.tool_access,
                'target_access':requested_by.role.target_access,
                'client_name_access':requested_by.role.client_name_access,
                'scan_result_access':requested_by.role.scan_result_access,
                'cover_content_access':requested_by.role.cover_content_access
            },
            "subscription_id": requested_by.subscription_id
        }
        return data

class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ['id', 'plan_type', 'updated_at']