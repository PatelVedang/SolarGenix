from proj.base_serializer import BaseSerializerValidator

from .models import Todo


class TodoSerializer(BaseSerializerValidator):
    # name = serializers.CharField(
    #     error_messages={"required": "The name field is mandasstory."}
    # )
    # price = serializers.DecimalField(
    #     max_digits=10,
    #     decimal_places=2,
    #     error_messages={
    #         "invalid": "Please provide a valid price.",
    #         "max_digits": "Price should not exceed 10 digits.",
    #     },
    # )

    class Meta:
        model = Todo
        fields = "__all__"
