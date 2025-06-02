#!/bin/bash

# Usage: ./scripts/rest_generator.sh APP_NAME
# clear the screen
clear
echo " ____  _                         "
echo "|  _ \\(_) __ _ _ __   __ _  ___  "
echo "| | | | |/ _\` | '_ \\ / _\` |/ _ \\ "
echo "| |_| | | (_| | | | | (_| | (_) |"
echo "|____// |\\__,_|_| |_|\\__, |\\___/ "
echo "    |__/             |___/       "
echo " ____        _ _                 _       _       "
echo "| __ )  ___ (_) | ___ _ __ _ __ | | __ _| |_ ___ "
echo "|  _ \\ / _ \\| | |/ _ \\ '__| '_ \\| |/ _\` | __/ _ \\"
echo "| |_) | (_) | | |  __/ |  | |_) | | (_| | ||  __/"
echo "|____/ \\___/|_|_|\\___|_|  | .__/|_|\\__,_|\\__\\___|"
echo "                          |_|                    "

# Get the current directory name
current_dir=$(basename "$PWD")

# Check if the current directory is not 'app'
if [ "$current_dir" != "app" ]; then
    echo "Error: This script must be run from the app/ directory."
    exit 1
fi


# Check if the app name argument is provided
if [ -z "$1" ]; then
    echo "Error: No app name provided."
    echo "Usage: ./scripts/rest_generator.sh APP_NAME"
    exit 1
fi

APP_NAME=$1
PROJECT_ROOT="."
SETTINGS_FILE="$PROJECT_ROOT/proj/settings.py"
URLS_FILE="$PROJECT_ROOT/proj/urls.py"
APP_PATH="$PROJECT_ROOT/$APP_NAME"

# Activate virtual environment
source ../env/bin/activate

echo "Initializing script..."

# Call name_generator.py to get naming conventions
NAMES_JSON=$(python ./scripts/name_generator.py "$APP_NAME")
PLURAL_UNDERSCORED=$(echo $NAMES_JSON | jq -r '.plural_underscored')
SINGULAR_CAPITALIZED=$(echo $NAMES_JSON | jq -r '.singular_capitalized')
SINGULAR_CAPITALIZED_SERIALIZER=$(echo $NAMES_JSON | jq -r '.singular_capitalized')Serializer
SINGULAR_CAPITALIZED_VIEWSET=$(echo $NAMES_JSON | jq -r '.singular_capitalized')ViewSet
SINGULAR_CAPITALIZED_MODEL_TESTS=$(echo $NAMES_JSON | jq -r '.singular_capitalized')ModelTests
SINGULAR_CAPITALIZED_ADMIN=$(echo $NAMES_JSON | jq -r '.singular_capitalized')Admin
PLURAL_DASHED=$(echo $NAMES_JSON | jq -r '.plural_dashed')
PLURAL_SPACE_SEPRATED=$(echo $NAMES_JSON | jq -r '.plural_space_separated')

# Check if the app already exists
if [ -d "$APP_PATH" ]; then
    echo "Error: The app '$PLURAL_UNDERSCORED' already exists."
    exit 1
fi

# Before running python manage.py startapp, check if there are any error
if ! python manage.py check; then
    echo "Error: 'python manage.py check' failed. Please fix all above issues the issues and then try again."
    exit 1
fi

# Check if the line '# django apps' exists in the file
if ! grep -q "# django apps" "$SETTINGS_FILE"; then
    echo "Error: Line '# django apps' does not exist in the file '$SETTINGS_FILE'."
    exit 1
fi

# Check if the line '# IMPORT_NEW_ROUTE_HERE' exists in the file
if ! grep -q "# IMPORT_NEW_ROUTE_HERE" "$URLS_FILE"; then
    echo "Error: Line '# IMPORT_NEW_ROUTE_HERE' does not exist in the file '$URLS_FILE'."
    exit 1
fi


# Create the Django app
echo "Task initiated: Creating Django app..."
python manage.py startapp "$PLURAL_UNDERSCORED"

# Determine the correct sed command for in-place editing
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    SED_CMD="sed -i ''"
else
    # Linux
    SED_CMD="sed -i"
fi

# Add the app to INSTALLED_APPS
if ! grep -q "'$PLURAL_UNDERSCORED'" "$SETTINGS_FILE"; then
    echo "Task initiated: Adding app to INSTALLED_APPS..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "/# django apps/a\\
    '$PLURAL_UNDERSCORED',\\
" "$SETTINGS_FILE"
    else
        # Linux
        sed -i "/# django apps/a\    '$PLURAL_UNDERSCORED'," "$SETTINGS_FILE"
    fi
    # $SED_CMD "/# django apps/a\    '$PLURAL_UNDERSCORED'," "$SETTINGS_FILE"
fi

# Add the app's URLs to the project's URLs
if ! grep -q "'$PLURAL_UNDERSCORED.urls'" "$URLS_FILE"; then
    echo "Task initiated: Adding app URLs to project URLs..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "/# IMPORT_NEW_ROUTE_HERE/a\\
    path(\"\", include('$PLURAL_UNDERSCORED.urls')),\\
" "$URLS_FILE"        
    else
        # Linux
        sed -i "/# IMPORT_NEW_ROUTE_HERE/a\                path(\"\", include('$PLURAL_UNDERSCORED.urls'))," "$URLS_FILE"
    fi
fi

# Generate models.py with various field types
echo "Task initiated: Generating models.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/models.py"
from django.db import models
import uuid
from proj.models import BaseModel

class $SINGULAR_CAPITALIZED(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.IntegerField()
    available = models.BooleanField(default=True)
    published_date = models.DateField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=1)
    image = models.ImageField(upload_to='images/',null=True,blank=True)
    file = models.FileField(upload_to='files/',null=True,blank=True)
    url = models.URLField(default='http://test.com')
    email = models.EmailField(default='test@yopmail.com')
    slug = models.SlugField(default='test-slug')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(default='127.0.0.1')
    big_integer = models.BigIntegerField(default='0')
    positive_integer = models.PositiveIntegerField(default='1')
    small_integer = models.SmallIntegerField(default='0')
    duration = models.DurationField(default='00:00:00')
    json_data = models.JSONField(default=dict)

    def __str__(self):
        return self.name
EOL

# Generate serializers.py
echo "Task initiated: Generating serializers.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/serializers.py"
from rest_framework import serializers
from proj.base_serializer import BaseModelSerializer
from .models import $SINGULAR_CAPITALIZED

class $SINGULAR_CAPITALIZED_SERIALIZER(BaseModelSerializer):
    class Meta:
        model = $SINGULAR_CAPITALIZED
        fields = '__all__'
EOL

# Generate views.py
echo "Task initiated: Generating views.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/views.py"
from utils.swagger import apply_swagger_tags
from utils.custom_filter import filter_model
from proj.base_view import BaseModelViewSet
from .models import $SINGULAR_CAPITALIZED
from .serializers import $SINGULAR_CAPITALIZED_SERIALIZER
from auth_api.permissions import IsAuthenticated
from rest_framework.decorators import action
from utils.make_response import response

@apply_swagger_tags(
    tags=["$PLURAL_SPACE_SEPRATED"],
    extra_actions=["get_all"],
    method_details={
        "get_all": {
            "description": "Get all $PLURAL_SPACE_SEPRATED records without pagination",
            "summary": "Get all $PLURAL_SPACE_SEPRATED",
        },
    },
)
class $SINGULAR_CAPITALIZED_VIEWSET(BaseModelViewSet):
    queryset = $SINGULAR_CAPITALIZED.objects.all()
    serializer_class = $SINGULAR_CAPITALIZED_SERIALIZER
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params
        if query_params:
            # Apply filtering based on query parameters
            return filter_model(query_params, queryset, $SINGULAR_CAPITALIZED)
        return queryset
    
    @action(methods=["GET"], detail=False, url_path="all")
    def get_all(self, request, *args, **kwargs):
        self.pagination_class = None
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return response(
            data=serializer.data,
            message=self.get_message(request, *args, **kwargs),
            status_code=200,
        )
EOL

# Generate urls.py
echo "Task initiated: Generating urls.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/urls.py"
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import $SINGULAR_CAPITALIZED_VIEWSET

router = DefaultRouter(trailing_slash=True)
router.register(r'', $SINGULAR_CAPITALIZED_VIEWSET)

urlpatterns = [
    path('$PLURAL_DASHED/', include(router.urls)),
]
EOL

# Generate admin.py
echo "Task initiated: Generating admin.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/admin.py"
from django.contrib import admin
from .models import $SINGULAR_CAPITALIZED

@admin.register($SINGULAR_CAPITALIZED)
class $SINGULAR_CAPITALIZED_ADMIN(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'inventory', 'available', 'published_date')
    search_fields = ('name', 'description', 'price', 'inventory', 'available', 'published_date')
EOL

# Generate tests.py
echo "Task initiated: Generating tests.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/tests.py"
import os,json, tempfile
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from datetime import date
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from .models import $SINGULAR_CAPITALIZED
from auth_api.models import User
from auth_api.tests import BaseAPITestCase



class ${SINGULAR_CAPITALIZED_MODEL_TESTS}(BaseAPITestCase):
    url = reverse("${APP_NAME}-list")
    
    def create_${APP_NAME}_via_orm(self, **kwargs):
        """Create a ${APP_NAME} using Django ORM and return the instance."""
        # Default valid data
        data = {
            "name": "New ${APP_NAME}",
            "description": "New description",
            "price": 10.99,
            "inventory": 15,
            "published_date": "2024-07-02",
            "rating": 4.7,
            "url": "http://example.com/new",
            "email": "new@example.com",
            "slug": "new-${APP_NAME}",
            "ip_address": "127.0.0.1",
            "big_integer": 8888888888,
            "positive_integer": 15,
            "small_integer": 7,
            "duration": "02:00:00",
            "json_data": json.dumps(
                {"key": "value", "key2": "value2"}
            ),  # Add JSON data as string
        }
        data.update(kwargs)

        # Attempt to create the ${APP_NAME} using Django's ORM and return the instance
        return ${SINGULAR_CAPITALIZED}.objects.create(**data)
    
    
    def test_create_${APP_NAME}_with_authenticate(self):
        """
        The function \`test_create_${APP_NAME}_with_authenticate\` creates a todo with authentication
        and checks for a successful response.
        """
        self.login()
        self.create_${APP_NAME}_via_orm()
        self.status_code = status.HTTP_201_CREATED

        self.match_success_response(201)

    def test_create_${APP_NAME}_without_authenticate(self):
        """
        The function \`test_create_${APP_NAME}_without_authenticate\` creates a todo without authentication
        and checks for a successful response.
        """
        self.create_${APP_NAME}_via_orm()
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.match_error_response(401)

    def test_create_${APP_NAME}_with_invalid_data(self):
        """
        The function \`test_create_${APP_NAME}_with_invalid_data\`
        and checks for a successful response.
        """
        self.login()
        invalid_data = {
            "url": "invalid_url"  # Invalid URL format
        }
        with self.assertRaises(Exception):  # Expect failure due to invalid data
            self.create_${APP_NAME}_via_orm(**invalid_data)
            self.match_error_response(400)

    def test_get_${APP_NAME}(self):
        """
        The function \`test_create_${APP_NAME}\` retrieves all ${APP_NAME} and checks for a successful response.
        """
        self.login()
        self.set_response(self.client.get(self.url))
        self.match_success_response(200)

    def test_get_${APP_NAME}_without_authenticate(self):
        """
        The function \`test_get_${APP_NAME}_without_authenticate\` retrieves all ${APP_NAME} without authentication
        and checks for a successful response.
        """
        self.set_response(self.client.get(self.url))
        self.match_error_response(401)

    def test_retrieve_${APP_NAME}_by_id(self):
        """
        The function \`test_retrieve_${APP_NAME}_by_id\` retrieves a ${APP_NAME} by ID and checks for a successful response.
        """
        self.login()
        ${APP_NAME} = self.create_${APP_NAME}_via_orm()
        created_${APP_NAME}_id = ${APP_NAME}.id
        self.set_response(self.client.get(f"{self.url}{created_${APP_NAME}_id}/"))
        self.match_success_response(200)

    def test_retrieve_${APP_NAME}_by_id_without_authenticate(self):
        """
        The function \`test_retrieve_${APP_NAME}_by_id_without_authenticate\` retrieves a ${APP_NAME} by ID without authentication
        and checks for a successful response.
        """
        ${APP_NAME} = self.create_${APP_NAME}_via_orm()
        created_${APP_NAME}_id = ${APP_NAME}.id
        self.set_response(self.client.get(f"{self.url}{created_${APP_NAME}_id}/"))
        self.match_error_response(401)

    def test_retrieve_${APP_NAME}_by_id_with_wrong_id(self):
        """
        The function \`test_retrieve_${APP_NAME}_by_id_without_authenticate\` retrieves a ${APP_NAME} by ID without authentication
        and checks for a successful response.
        """
        self.login()
        self.set_response(self.client.get(f"{self.url}1000/"))
        self.match_error_response(404)

    def test_update_${APP_NAME}_by_id(self):
        self.login()
        ${APP_NAME} = self.create_${APP_NAME}_via_orm()
        created_${APP_NAME}_id = ${APP_NAME}.id
        # Update the ${APP_NAME} with a patch request
        self.client.patch(
            f"{self.url}{created_${APP_NAME}_id}/", {"name": "Updated name"}, format="json"
        )
        self.match_success_response()

    def test_update_${APP_NAME}_by_id_without_authenticate(self):
        ${APP_NAME} = self.create_${APP_NAME}_via_orm()
        # Update the ${APP_NAME} with a patch request
        self.client.patch(
            f"{self.url}{${APP_NAME}.id}/", {"name": "Updated name"}, format="json"
        )
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.match_error_response(401)

    def test_update_${APP_NAME}_by_id_with_wrong_id(self):
        self.login()

        self.set_response(
            self.client.patch(
                f"{self.url}1000/", {"name": "Updated name"}, format="json"
            )
        )
        self.match_error_response(404)

    # def test_create_${APP_NAME}_with_invalid_email(self):
    #     """Test creating ${APP_NAME} with invalid email."""
    #     self.login()
    #     payload = {
    #         "name": "Test Todo",  # Adjust these fields as needed
    #         "email": "invalid-email",
    #     }
    #     self.create_todo_via_orm(**payload)
    #     self.status_code = status.HTTP_400_BAD_REQUEST
    #     self.match_error_response(400)

    # def test_create_${APP_NAME}_with_existing_email(self):
    #     """
    #     Test creating ${APP_NAME} with an existing email, expecting a 400 Bad Request error using ORM.
    #     """
    #     self.login()
    #     # Create the first todo via ORM
    #     self.create_todo_via_orm(email="duplicate@example.com")
    #     # self.create_todo_via_orm(email="duplicate@example.com")
    #     if Todo.objects.filter(email="duplicate@example.com").count() > 1:
    #         # Simulate a 400 Bad Request error since email is already in use
    #         self.match_error_response(400)
    #     else:
    #         # Create the second todo via ORM (this shouldn't be reached in this test)
    #         self.create_todo_via_orm(email="duplicate@example.com")
    #         self.match_error_response(200)  # This line is for testing purposes

    def test_delete_${APP_NAME}_by_id(self):
        """
        The function \`test_delete_${APP_NAME}_by_id\` deletes a ${APP_NAME} by ID and checks for a successful response.
        """
        self.login()
        ${APP_NAME} = self.create_${APP_NAME}_via_orm()
        created_${APP_NAME}_id = ${APP_NAME}.id
        self.set_response(self.client.delete(f"{self.url}{created_${APP_NAME}_id}/"))
        self.match_success_response(204)

    def test_delete_${APP_NAME}_by_id_without_authenticate(self):
        #     """Test deleting by ID without authentication."""
        ${APP_NAME} = self.create_${APP_NAME}_via_orm()
        created_${APP_NAME}_id = ${APP_NAME}.id
        self.set_response(self.client.delete(f"{self.url}{created_${APP_NAME}_id}/"))
        self.match_error_response(401)

    def test_delete_${APP_NAME}_by_id_with_wrong_id(self):
        """Test deleting a ${APP_NAME} by an invalid ID."""
        self.login()
        self.set_response(self.client.delete(f"{self.url}111/"))
        self.match_error_response(404)


EOL

# Ensure settings file is saved and changes are applied
sleep 2

# Make migrations and migrate
python manage.py makemigrations "$PLURAL_UNDERSCORED"
python manage.py migrate

echo "App '$PLURAL_UNDERSCORED' has been created and configured successfully."
echo "App '$PLURAL_UNDERSCORED' created successfully!"