from proj.base_serializer import DynamicFieldsSerializer
from .models import Demo


class DemoSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Demo
        fields = "__all__"
