import pandas as pd
from core.models import User
from django.http import HttpResponse, JsonResponse
from users.constants import UserResponseConstants


class ExportUsersService:
    """Service to handle exporting user data in various formats. like CSV or JSON."""

    def post_execute(self, request):
        export_fields = request.query_params.get("export_fields", "")
        export_format = request.query_params.get("export_format", "csv").lower()

        default_fields = [
            field.name
            for field in User._meta.get_fields()
            if field.concrete and not field.many_to_many and not field.one_to_many
        ]

        selected_fields = (
            [
                field.strip()
                for field in export_fields.split(",")
                if field.strip() in default_fields
            ]
            if export_fields
            else default_fields
        )

        if not selected_fields:
            return JsonResponse(
                {"error": UserResponseConstants.INVALID_FIELDS}, status=400
            )

        users = User.objects.all().values(*selected_fields)

        df = pd.DataFrame(users)

        for field in df.columns:
            if "date" in field or "time" in field:
                df[field] = pd.to_datetime(df[field]).dt.strftime("%Y-%m-%d %H:%M:%S")

        if export_format == "csv":
            res = HttpResponse(content_type="text/csv")
            res["Content-Disposition"] = 'attachment; filename="users_export.csv"'
            df.to_csv(path_or_buf=res, index=False)
            return res
        elif export_format == "json":
            return JsonResponse(df.to_dict(orient="records"), safe=False, status=200)
        else:
            return JsonResponse(
                {"error": UserResponseConstants.INVALID_EXPORT_FORMAT}, status=400
            )
