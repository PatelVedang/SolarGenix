from rest_framework import serializers
from .models import Machine, Tool
from django.core.validators import validate_ipv4_address

class ScannerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    ip = serializers.ListField(child=serializers.CharField(validators=[validate_ipv4_address]))
    client = serializers.CharField()
    tools_id = serializers.ListField(child=serializers.IntegerField())
    class Meta:
        model = Machine
        fields = ['ip','client','id','tools_id']

    def validate(self, attrs):
        tools_id = attrs['tools_id']
        for tool_id in tools_id:
            if not Tool.objects.filter(id=tool_id).exists():
                raise serializers.DjangoValidationError(f"Tool does not exist with id {tool_id}")
        return super().validate(attrs)

class ScannerResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tool']= instance.tool.tool_name
        return data