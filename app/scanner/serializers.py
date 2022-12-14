from rest_framework import serializers
from .models import Machine, TOOL_CHOICES
from django.core.validators import validate_ipv4_address

class ScannerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    ip = serializers.ListField(child=serializers.CharField(validators=[validate_ipv4_address]))
    client = serializers.CharField()
    tool = serializers.ChoiceField(choices=TOOL_CHOICES, default='nmap')
    class Meta:
        model = Machine
        fields = ['ip','client','id','tool']

class ScannerResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'