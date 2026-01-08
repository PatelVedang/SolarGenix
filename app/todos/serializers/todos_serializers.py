from rest_framework import serializers
from proj.base_serializer import BaseModelSerializer
from core.models import Todos

class TodosSerializer(BaseModelSerializer):
    class Meta:
        model = Todos
        fields = '__all__'
