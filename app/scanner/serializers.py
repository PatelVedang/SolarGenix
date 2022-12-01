from rest_framework import serializers
from .models import Machine
from django.core.validators import validate_ipv4_address

class IpSerializer(serializers.ModelSerializer):
    ip = serializers.CharField(validators=[validate_ipv4_address])
    class Meta:
        model = Machine
        fields = ['ip']