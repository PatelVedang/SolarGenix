from proj.base_serializer import DynamicFieldsSerializer
from .models import Product


class ProductSerializer(DynamicFieldsSerializer):
    class Meta:
        model = Product
        fields = "__all__"
