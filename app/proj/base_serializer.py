from rest_framework import serializers


class BaseErrorFormatter:
    def format_errors(self, errors, fields, parent_field=None, parent_index=None):
        new_errors = {}
        for field, error_list in errors.items():
            if field == "non_field_errors":
                # Handle non_field_errors separately
                new_errors[field] = self.format_error_messages(error_list, field, field)
            elif isinstance(error_list, list):
                if isinstance(error_list[0], dict):
                    # Handling nested serializer errors (list of dictionaries)
                    for idx, nested_error in enumerate(error_list):
                        nested_field = (
                            fields[field].child
                            if hasattr(fields[field], "child")
                            else fields[field]
                        )
                        formatted_nested_errors = self.format_errors(
                            nested_error,
                            nested_field.fields,
                            parent_field=field,
                            parent_index=idx,
                        )
                        for key, value in formatted_nested_errors.items():
                            new_key = f"{field}[{idx}].{key}"
                            new_errors[new_key] = value
                else:
                    # Handle errors that are just a list of strings
                    field_label = fields[field].label if fields[field].label else field
                    for idx, error in enumerate(error_list):
                        new_errors[f"{field}[{parent_index}]"] = (
                            self.format_error_messages(
                                [error],
                                field,
                                field_label,
                                index=parent_index,
                                parent_field=parent_field,
                            )
                        )

            elif isinstance(error_list, dict):
                # Handling nested serializer errors (dictionary)
                nested_field = fields[field]
                if isinstance(nested_field, serializers.ListSerializer):
                    nested_field = nested_field.child
                new_errors.update(
                    self.format_errors(
                        error_list,
                        nested_field.fields,
                        parent_field=field,
                        parent_index=parent_index,
                    )
                )
        return new_errors

    def format_error_messages(
        self, error_list, field, field_label, index=None, parent_field=None
    ):
        for error in error_list:
            code = error.code
            original_label = field_label
            if index is not None and parent_field is not None:
                field_label = f"{field_label} at index {index} of {parent_field}"

            if code == "required" and "__custom" not in str(error):
                message = f"{field_label} field is required."
            elif code == "null" and "__custom" not in str(error):
                message = f"{field_label} field cannot be null."
            elif code == "blank" and "__custom" not in str(error):
                message = f"{field_label} field cannot be blank."
            elif code == "does_not_exist" and "__custom" not in str(error):
                message = f"{field_label} field does not exist with the provided value."
            elif code == "unique" and "__custom" not in str(error):
                message = f"{field_label} field already exists."
            elif code == "invalid" and "__custom" not in str(error):
                message = f"{field_label} field is invalid."
            elif code == "invalid_choice" and "__custom" not in str(error):
                message = f"{field_label} field is an invalid choice."
            else:
                if "__custom" in str(error):
                    message = str(error).replace("__custom", "")
                else:
                    message = str(error)

            return {"key": field, "label": original_label, "message": message}
        return {}


class BaseSerializer(BaseErrorFormatter, serializers.Serializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def run_validation(self, data):
        try:
            return super().run_validation(data)
        except serializers.ValidationError as exc:
            errors = exc.detail
            new_errors = self.format_errors(errors, self.fields)
            raise serializers.ValidationError(new_errors)

    def to_representation(self, instance):
        if isinstance(instance, dict):
            return instance
        return super().to_representation(instance)


class BaseModelSerializer(BaseErrorFormatter, serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def run_validation(self, data):
        try:
            return super().run_validation(data)
        except serializers.ValidationError as exc:
            errors = exc.detail
            new_errors = self.format_errors(errors, self.fields)
            raise serializers.ValidationError(new_errors)
