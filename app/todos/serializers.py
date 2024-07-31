from dataclasses import fields
from rest_framework import serializers
from .models import Todo

class TodoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Todo
        # fields = ['name','email','url','slug']
        fields = '__all__'
    def to_representation(self, instance):
        if isinstance(instance, dict):
            return instance
        return super().to_representation(instance)