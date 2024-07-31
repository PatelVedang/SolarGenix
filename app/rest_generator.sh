#!/bin/bash

# Usage: ./scripts/rest_generator.sh APP_NAME
#clear the screen
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
SINGULAR_CAPITALIZED_VIEWSET=$(echo $NAMES_JSON | jq -r '.singular_capitalized')Viewset
SINGULAR_CAPITALIZED_MODEL_TESTS=$(echo $NAMES_JSON | jq -r '.singular_capitalized')ModelTests
SINGULAR_CAPITALIZED_ADMIN=$(echo $NAMES_JSON | jq -r '.singular_capitalized')Admin
PLURAL_DASHED=$(echo $NAMES_JSON | jq -r '.plural_dashed')

# Check if the app already exists
if [ -d "$APP_PATH" ]; then
    echo "Error: The app '$PLURAL_UNDERSCORED' already exists."
    exit 1
fi

# Create the Django app
echo "Task initiated: Creating Django app..."
python manage.py startapp "$PLURAL_UNDERSCORED"

# Add the app to INSTALLED_APPS
if ! grep -q "'$PLURAL_UNDERSCORED'" "$SETTINGS_FILE"; then
    echo "Task initiated: Adding app to INSTALLED_APPS..."
    sed -i "/INSTALLED_APPS = \[/a\    '$PLURAL_UNDERSCORED'," "$SETTINGS_FILE"
fi

# Add the app's URLs to the project's URLs
if ! grep -q "'$PLURAL_UNDERSCORED'" "$URLS_FILE"; then
    echo "Task initiated: Adding app URLs to project URLs..."
    sed -i "/path('swagger',/i\        path('api/$PLURAL_DASHED/', include('$PLURAL_UNDERSCORED.urls'))," "$URLS_FILE"
fi

# Generate models.py with various field types
echo "Task initiated: Generating models.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/models.py"
from django.db import models
import uuid

class $SINGULAR_CAPITALIZED(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.IntegerField()
    available = models.BooleanField(default=True)
    published_date = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField()
    image = models.ImageField(upload_to='images/')
    file = models.FileField(upload_to='files/')
    url = models.URLField()
    email = models.EmailField()
    slug = models.SlugField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField()
    big_integer = models.BigIntegerField()
    positive_integer = models.PositiveIntegerField()
    small_integer = models.SmallIntegerField()
    duration = models.DurationField()
    json_data = models.JSONField()

    def __str__(self):
        return self.name
EOL

# Generate serializers.py
echo "Task initiated: Generating serializers.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/serializers.py"
from rest_framework import serializers
from proj.base_serializer import DynamicFieldsSerializer
from .models import $SINGULAR_CAPITALIZED

class $SINGULAR_CAPITALIZED_SERIALIZER(DynamicFieldsSerializer):
    class Meta:
        model = $SINGULAR_CAPITALIZED
        fields = '__all__'
EOL

# Generate views.py
echo "Task initiated: Generating views.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/views.py"
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from utils.swagger import apply_swagger_tags
from proj.base_view import BaseModelViewSet
from .models import $SINGULAR_CAPITALIZED
from .serializers import $SINGULAR_CAPITALIZED_SERIALIZER


class $SINGULAR_CAPITALIZED_VIEWSET(BaseModelViewSet):
    queryset = $SINGULAR_CAPITALIZED.objects.all()
    serializer_class = $SINGULAR_CAPITALIZED_SERIALIZER
    permission_classes = [IsAuthenticated]
EOL

# Generate urls.py
echo "Task initiated: Generating urls.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/urls.py"
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import $SINGULAR_CAPITALIZED_VIEWSET

router = DefaultRouter()
router.register(r'', $SINGULAR_CAPITALIZED_VIEWSET)

urlpatterns = [
    path('', include(router.urls)),
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
    search_fields = ('name', 'description', 'price')
    list_filter = ('available', 'published_date')
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


class $SINGULAR_CAPITALIZED_MODEL_TESTS(TestCase):

    # def setUp(self):
    #     self.${APP_NAME}_instance = $SINGULAR_CAPITALIZED.objects.create(
    #         name="Test Name",
    #         description="Test description",
    #         price=9.99,
    #         inventory=100,
    #         available=True,
    #         published_date="2024-01-01",
    #         rating=4.5,
    #         url="https://example.com",
    #         email="test@example.com",
    #         slug="test-name",
    #         ip_address="127.0.0.1",
    #         big_integer=9999999999,
    #         positive_integer=123,
    #         small_integer=12,
    #         duration=timedelta(days=1),
    #         json_data={"key": "value"}
    #     )

    # def test_${APP_NAME}_creation(self):
    #     self.assertIsInstance(self.${APP_NAME}_instance, $SINGULAR_CAPITALIZED)
    #     self.assertEqual(self.${APP_NAME}_instance.__str__(), self.${APP_NAME}_instance.name)
    def setUp(self):
        # Create a user and set the password
        self.user = User.objects.create_superuser(
            email='testuser@example.com',
            name='Test User',
            password='testpass123',
            tc=True,
        )
        self.user.is_active = True
        self.user.save()

        # Authenticate the user and obtain the token
        self.client = APIClient()
        login_response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }, format='json')
        
        # Extract access token
        self.access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

        # Create a temporary image for testing
        self.image = self.generate_test_image()
        # Create a temporary file for testing
        self.file, self.file_path = self.generate_test_file()
        
        # Set up a ${APP_NAME} instance
        self.${APP_NAME} = ${SINGULAR_CAPITALIZED}.objects.create(
            name='Test Name',
            description='Test description',
            price=9.99,
            inventory=10,
            published_date=date(2024, 7, 1),
            rating=4.5,
            url='http://example.com',
            email='info@example.com',
            slug='test-${APP_NAME}',
            ip_address='127.0.0.1',
            big_integer=9999999999,
            positive_integer=10,
            small_integer=5,
            duration='01:00:00',
            json_data={"key": "value"},
            image=self.image,
            file=self.file,
        )

    def generate_test_image(self):
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image:
            image = Image.new("RGB", (100, 100), color=(255, 0, 0))
            image.save(temp_image, format='PNG')
            temp_image.seek(0)
            return SimpleUploadedFile(temp_image.name, temp_image.read(), content_type='image/png')

    def generate_test_file(self):
        # Create a temporary file
        file_content = b'This is a test file.'
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(file_content)
        temp_file.flush()
        temp_file.seek(0)  # Go back to the start of the file for reading
        return SimpleUploadedFile(temp_file.name, temp_file.read(), content_type='text/plain'), temp_file.name

    def test_create_${APP_NAME}_authentication(self):
        url = reverse('${APP_NAME}-list')  # Ensure this URL name matches your URL pattern

        # Flatten or serialize JSON data
        json_data_str = json.dumps({"key": "new value"})

        sample_image = self.generate_test_image()
        test_file = self.generate_test_file()
        data = {
            "name": "New ${PLURAL_UNDERSCORED}",
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
            "json_data": json_data_str,  # Pass JSON data as string
            "image": sample_image,  # Add image here
            "file": test_file,  # Add file here
        }

        response = self.client.post(url, data, format='multipart')
        data = response.data.get("data", None)
        ${APP_NAME}_id = data.get("id") if data else None
        if ${APP_NAME}_id:
            ${APP_NAME}_instance =${SINGULAR_CAPITALIZED}.objects.get(id=${APP_NAME}_id)
            if ${APP_NAME}_instance.image:
                ${APP_NAME}_instance.image.delete(save=False)
            if ${APP_NAME}_instance.file:
                ${APP_NAME}_instance.file.delete(save=False)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_${APP_NAME}_without_authentication(self):
        # Authenticate the user and obtain the token
        self.client = APIClient()
        self.client.credentials()
        url = reverse('${APP_NAME}-list')  # Ensure this URL name matches your URL pattern

        # Flatten or serialize JSON data
        json_data_str = json.dumps({"key": "new value"})

        sample_image = self.generate_test_image()
        test_file = self.generate_test_file()
        data = {
            "name": "New ${SINGULAR_CAPITALIZED}",
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
            "json_data": json_data_str,  # Pass JSON data as string
            "image": sample_image,  # Add image here
            "file": test_file,  # Add file here
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_${APP_NAME}_validation(self):
        # Authenticate the user and obtain the token
        url = reverse('${APP_NAME}-list')  # Ensure this URL name matches your URL pattern

        # Flatten or serialize JSON data
        json_data_str = json.dumps({"key": "new value"})

        sample_image = self.generate_test_image()
        test_file = self.generate_test_file()
        data = {
            "name": 123, # pass int value instead of str
            "description": "New description",
            "price": 10.99,
            "inventory": 15,
            "published_date": "2024-07-02",
            "rating": '4.7',
            "url": "example.com/new", #pass wrong field value
            "email": "new",
            "slug": "new-${APP_NAME}",
            "ip_address": "127.0.0.1",
            "big_integer": 8888888888,
            "positive_integer": 15,
            "small_integer": 7,
            "duration": "02:00:00",
            "json_data": json_data_str,  # Pass JSON data as string
            "image": sample_image,  # Add image here
            "file": test_file,  # Add file here
        }

        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_read_${APP_NAME}_authentication(self):
        url = reverse('${APP_NAME}-detail', args=[self.${APP_NAME}.id])  # Ensure this URL name matches your URL pattern

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], self.${APP_NAME}.name)
    
    def test_read_${APP_NAME}_without_authentication(self):
        # Authenticate the user and obtain the token
        self.client = APIClient()
        self.client.credentials()
        
        url = reverse('${APP_NAME}-detail', args=[self.${APP_NAME}.id])  # Ensure this URL name matches your URL pattern

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # self.assertEqual(response.data['data']['name'], self.${APP_NAME}.name)

    def test_read_${APP_NAME}_with_not_exists_id(self):
        url = reverse('${APP_NAME}-detail', args=[1231465])  # Ensure this URL name matches your URL pattern

        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # self.assertEqual(response.data['data']['name'], self.${APP_NAME}.name)
    
    def test_update_${APP_NAME}_authentication(self):
        url = reverse('${APP_NAME}-detail', args=[self.${APP_NAME}.id])  # Ensure this URL name matches your URL pattern

        updated_data = {
            "name": "Updated ${APP_NAME}",
            "description": "Updated description",
            "price": 11.99,
            "inventory": 20,
            "published_date": "2024-07-03",
            "rating": 4.9,
            "url": "http://example.com/updated",
            "email": "updated@example.com",
            "slug": "updated-${APP_NAME}",
            "ip_address": "127.0.0.2",
            "big_integer": 7777777777,
            "positive_integer": 20,
            "small_integer": 10,
            "duration": "03:00:00",
            "json_data": json.dumps({"key": "updated value"}),  # Pass JSON data as string
            "image": self.generate_test_image(),  # Add updated image here
            "file": self.generate_test_file(),  # Add updated file here
        }

        response = self.client.patch(url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], updated_data['name'])

    def test_update_${APP_NAME}_without_authentication(self):
        # Authenticate the user and obtain the token
        self.client = APIClient()
        self.client.credentials()

        url = reverse('${APP_NAME}-detail', args=[self.${APP_NAME}.id])  # Ensure this URL name matches your URL pattern
        
        updated_data = {
            "name": "Updated ${SINGULAR_CAPITALIZED}",
            "description": "Updated description",
            "price": 11.99,
            "inventory": 20,
            "published_date": "2024-07-03",
            "rating": 4.9,
            "url": "http://example.com/updated",
            "email": "updated@example.com",
            "slug": "updated-${APP_NAME}",
            "ip_address": "127.0.0.2",
            "big_integer": 7777777777,
            "positive_integer": 20,
            "small_integer": 10,
            "duration": "03:00:00",
            "json_data": json.dumps({"key": "updated value"}),  # Pass JSON data as string
            "image": self.generate_test_image(),  # Add updated image here
            "file": self.generate_test_file(),  # Add updated file here
        }

        response = self.client.patch(url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_${APP_NAME}_validation(self):
        url = reverse('${APP_NAME}-detail', args=[self.${APP_NAME}.id])  # Ensure this URL name matches your URL pattern
        
        updated_data = {
            "url":"worng value"
        }

        response = self.client.patch(url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_${APP_NAME}_with_not_exists_id(self):
        url = reverse('${APP_NAME}-detail', args=[0])  # Ensure this URL name matches your URL pattern
        
        updated_data = {
            "name": "Updated ${SINGULAR_CAPITALIZED}",
            "description": "Updated description",
            "price": 11.99,
            "inventory": 20,
            "published_date": "2024-07-03",
            "rating": 4.9,
            "url": "http://example.com/updated",
            "email": "updated@example.com",
            "slug": "updated-${APP_NAME}",
            "ip_address": "127.0.0.2",
            "big_integer": 7777777777,
            "positive_integer": 20,
            "small_integer": 10,
            "duration": "03:00:00",
            "json_data": json.dumps({"key": "updated value"}),  # Pass JSON data as string
            "image": self.generate_test_image(),  # Add updated image here
            "file": self.generate_test_file(),  # Add updated file here
        }

        response = self.client.patch(url, updated_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_partial_update_${APP_NAME}_authenticated(self):
        url = reverse('${APP_NAME}-detail', args=[self.${APP_NAME}.id])  # Ensure this URL name matches your URL pattern

        updated_data = {
            "name": "Partially Updated ${SINGULAR_CAPITALIZED}"
        }

        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], updated_data['name'])

    def test_partial_update_${APP_NAME}_without_authentication(self):
        # Authenticate the user and obtain the token
        self.client = APIClient()
        self.client.credentials()
        
        url = reverse('${APP_NAME}-detail', args=[self.${APP_NAME}.id])  # Ensure this URL name matches your URL pattern

        updated_data = {
            "name": "Partially Updated ${SINGULAR_CAPITALIZED}"
        }

        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_${APP_NAME}_validation(self):
        url = reverse('${APP_NAME}-detail', args=[self.${APP_NAME}.id])  # Ensure this URL name matches your URL pattern

        updated_data = {
            "url": "Partially Updated ${SINGULAR_CAPITALIZED}"
        }

        response = self.client.patch(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_${APP_NAME}_authenticated(self):
        url = reverse('${APP_NAME}-detail', args=[self.${APP_NAME}.id])  # Ensure this URL name matches your URL pattern

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(${SINGULAR_CAPITALIZED}.objects.filter(id=self.${APP_NAME}.id).exists())
    
    def test_delete_${APP_NAME}_without_authentication(self):
        # Authenticate the user and obtain the token
        self.client = APIClient()
        self.client.credentials()

        url = reverse('${APP_NAME}-detail', args=[self.${APP_NAME}.id])  # Ensure this URL name matches your URL pattern

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_${APP_NAME}_not_exists_id(self):
        url = reverse('${APP_NAME}-detail', args=[0])  # Ensure this URL name matches your URL pattern

        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_list_all_${APP_NAME}(self):
        self.access_token = ''
        url = reverse('${APP_NAME}-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        # Delete temporary files after the test
        self.${APP_NAME}.image.delete(save=False)  # Delete the image file if it was saved to media
        self.${APP_NAME}.file.delete(save=False)   # Delete the file if it was saved to media
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
EOL

# Ensure settings file is saved and changes are applied
sleep 2

# Make migrations and migrate
python manage.py makemigrations "$PLURAL_UNDERSCORED"
python manage.py migrate

echo "App '$PLURAL_UNDERSCORED' has been created and configured successfully."
