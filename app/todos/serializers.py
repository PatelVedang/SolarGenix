from proj.base_serializer import BaseModelSerializer

from .models import Todo


class TodoSerializer(BaseModelSerializer):
    class Meta:
        model = Todo
        fields = "__all__"
