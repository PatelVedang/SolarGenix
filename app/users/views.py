from auth_api.models import User
from auth_api.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from proj.base_view import BaseModelViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from utils.custom_filter import filter_model
from utils.make_response import response
from utils.swagger import apply_swagger_tags
from .permission import CustomSuperAdminOrOwnerDeletePermission
from .serializers import UserSerializer ,UserExportSerializer
from rest_framework.views import APIView
import pandas as pd
from django.http import HttpResponse ,JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

@apply_swagger_tags(
    tags=["Users"],
    extra_actions=["get_all"],
    method_details={
        "get_all": {
            "description": "Get all user records without pagination",
            "summary": "Get all users",
        },
    },
)
class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Customize permissions based on the action
        if self.action == "destroy":
            return [
                CustomSuperAdminOrOwnerDeletePermission(),
            ]  # Replace with your custom permission class
        return super().get_permissions()

    def get_queryset(self):
        queryset = (
            User.objects.all()
            if self.request.user.is_superuser
            else User.objects.filter(id=self.request.user.id)
        )
        query_params = self.request.query_params
        if query_params:
            # Apply filtering based on query parameters
            return filter_model(query_params, queryset, User)
        return queryset

    def create(self, request, *args, **kwargs):
        # Check if the user is a superuser
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can create users.")

        # If superuser, proceed with the default create behavior
        return super().create(request, *args, **kwargs)

    @action(methods=["GET"], detail=False, url_path="get_all")
    def get_all(self, request, *args, **kwargs):
        self.pagination_class = None
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return response(
            data=serializer.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=200,
        )

    @extend_schema( 
    summary="Export Users Data",
    description="Export user data in CSV or JSON format using query parameters.",
    parameters=[
        OpenApiParameter(
            name="export_fields",
            description=(
                'Comma-separated list of fields to export. '
                f'Available: {", ".join([field.name for field in queryset.model._meta.get_fields() if field.concrete and not field.many_to_many and not field.one_to_many])}'
            ),
            required=False,
            type=OpenApiTypes.STR,
            
        ),
        OpenApiParameter(
            name="export_format",
            description="Format to export data",
            required=False,
            type=OpenApiTypes.STR,
            enum=["csv", "json"], 
        ),
    ],
    responses={200: UserExportSerializer(many=True)},
    )
    @action(methods=["GET"], detail=False, url_path="export-users" ,permission_classes=[IsAdminUser])
    def export_users(self, request, *args, **kwargs):
        export_fields = request.query_params.get("export_fields" ,"")
        export_format = request.query_params.get("export_format", "csv").lower()
        
        default_fields = [field.name for field in User._meta.get_fields() if field.concrete and not field.many_to_many and not field.one_to_many]
        
        selected_fields = [field.strip() for field in export_fields.split(",") if field.strip() in default_fields] if export_fields else default_fields
        
        if not selected_fields:
            return JsonResponse({"error": "No valid fields specified."}, status=400)

        users = User.objects.all().values(*selected_fields)

        df = pd.DataFrame(users)

        for field in df.columns:
            if "date" in field or "time" in field:
                df[field] = pd.to_datetime(df[field]).dt.strftime("%Y-%m-%d %H:%M:%S")
                
        if export_format == "csv":
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = 'attachment; filename="users_export.csv"'
            df.to_csv(path_or_buf=response, index=False)
            return response
        
        elif export_format == "json":
            return JsonResponse(df.to_dict(orient="records"), safe=False)
        else:
            return JsonResponse({"error": "Invalid export format. Choose from csv, json."}, status=400)
            
