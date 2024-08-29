from proj.base_view import BaseModelViewSet
from rest_framework.permissions import IsAuthenticated
from utils.custom_filter import filter_model

from .models import Product
from .serializers import ProductSerializer


# @apply_swagger_tags(
#     tags=["Product"],
#     extra_actions=["get_all"],
#     method_details={
#         "get_all": {
#             "operation_description": "Get all Products records without pagination",
#             "operation_summary": "Get all Products",
#         },
#     },
# )
class ProductViewset(BaseModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params
        if query_params:
            # Apply filtering based on query parameters
            return filter_model(query_params, queryset, Product)
        return queryset
        return queryset
