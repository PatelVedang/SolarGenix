from rest_framework import serializers
from .models import Machine, Tool
from user.models import User
from django.core.validators import validate_ipv4_address

# This class is a serializer for the Machine model. It has a custom validation method that checks if
# the tools_id field is a list of integers that correspond to existing Tool objects
class ScannerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    ip = serializers.ListField(child=serializers.CharField(validators=[validate_ipv4_address]))
    tools_id = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    class Meta:
        model = Machine
        fields = ['ip','id','tools_id']

    def validate(self, attrs):
        tools_id = attrs['tools_id']
        for tool_id in tools_id:
            if not Tool.objects.filter(id=tool_id).exists():
                raise serializers.DjangoValidationError(f"Tool does not exist with id {tool_id}")
        return super().validate(attrs)

# The ScannerResponseSerializer class is a subclass of the ModelSerializer class. It has a Meta class
# that specifies the model to be used and the fields to be serialized. The to_representation method is
# overridden to add the tool name to the serialized data
class ScannerResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tool']= Tool.objects.filter(id=instance.tool.id).values('id', 'tool_name', 'tool_cmd')[0]
        data['scan_by'] = User.objects.filter(id=instance.scan_by.id).values('id', 'email', 'first_name', 'last_name')[0]
        return data

# The ScannerQueueSerializer class is a serializer for the Machine model. It has a field called ids
# which is a list of integers
class AddInQueueByIdsSerializer(serializers.ModelSerializer):
    machines_id = serializers.ListField(child = serializers.IntegerField(), allow_empty=False)
    class Meta:
        model = Machine
        fields = ['machines_id']

    def validate(self, attrs):
        machines_id = attrs['machines_id']
        for machine_id in machines_id:
            if not Machine.objects.filter(id=machine_id).exists():
                raise serializers.DjangoValidationError(f"Machine does not exist with id {machine_id}")
        return super().validate(attrs)

class AddInQueueByNumbersSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()
    class Meta:
        model = Machine
        fields = ['count']


class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = '__all__'