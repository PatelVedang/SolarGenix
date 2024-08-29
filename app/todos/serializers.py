from proj.base_serializer import DynamicFieldsSerializer
from .models import Todo


class TodoSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Todo
        fields = "__all__"
