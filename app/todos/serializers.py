from proj.base_serializer import BaseModelSerializer

from core.models import Todo


class TodoSerializer(BaseModelSerializer):
    class Meta:
        model = Todo
        fields = "__all__"
