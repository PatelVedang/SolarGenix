from rest_framework import serializers


class BaseErrorFormatter:
    """
    BaseErrorFormatter provides utilities to format and standardize error messages
    from Django REST Framework serializers, especially for nested and complex
    serializer structures.

    Methods
    -------
    format_errors(errors, fields, parent_field=None, parent_index=None)
        Recursively formats serializer error dictionaries, handling nested serializers,
        lists of errors, and non-field errors. Returns a flat dictionary mapping
        error keys to formatted error messages.

    format_error_messages(error_list, field, field_label, index=None, parent_field=None)
        Formats a list of error messages for a given field, generating user-friendly
        messages based on error codes (e.g., 'required', 'null', 'blank', etc.).
        Supports custom error messages and contextualizes errors for nested fields.
    """
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
    """
    BaseSerializer extends DRF's Serializer to provide dynamic field selection and custom error formatting.

    Args:
        fields (list, optional): A list of field names to include in the serialized output. If provided, only these fields will be present.

    Methods:
        __init__(*args, **kwargs):
            Initializes the serializer and optionally restricts the fields to those specified in the 'fields' argument.

        run_validation(data):
            Runs validation on the input data. If a ValidationError is raised, formats the errors using the custom error formatter before re-raising.

        to_representation(instance):
            Returns the representation of the instance. If the instance is a dict, returns it as-is; otherwise, uses the default representation logic.
    """
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
    """
    A base serializer class that extends Django REST Framework's ModelSerializer with additional functionality:

    - Allows dynamic inclusion of fields via the 'fields' keyword argument during initialization. Only the specified fields will be included in the serialized output.
    - Overrides the run_validation method to catch ValidationError exceptions and format the error messages using the format_errors method from BaseErrorFormatter.

    Args:
        *args: Variable length argument list for the parent serializer.
        **kwargs: Arbitrary keyword arguments. Supports an optional 'fields' argument (list or set of field names to include).

    Raises:
        serializers.ValidationError: If validation fails, with errors formatted by BaseErrorFormatter.
    """
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
