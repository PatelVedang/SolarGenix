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
from .models import $SINGULAR_CAPITALIZED

class $SINGULAR_CAPITALIZED_SERIALIZER(serializers.ModelSerializer):
    class Meta:
        model = $SINGULAR_CAPITALIZED
        fields = '__all__'
EOL

# Generate views.py
echo "Task initiated: Generating views.py..."
cat <<EOL > "$PLURAL_UNDERSCORED/views.py"
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import $SINGULAR_CAPITALIZED
from .serializers import $SINGULAR_CAPITALIZED_SERIALIZER

class $SINGULAR_CAPITALIZED_VIEWSET(viewsets.ModelViewSet):
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
from django.test import TestCase
from datetime import timedelta
from .models import $SINGULAR_CAPITALIZED

class $SINGULAR_CAPITALIZED_MODEL_TESTS(TestCase):

    def setUp(self):
        self.${APP_NAME}_instance = $SINGULAR_CAPITALIZED.objects.create(
            name="Test Name",
            description="Test description",
            price=9.99,
            inventory=100,
            available=True,
            published_date="2024-01-01",
            rating=4.5,
            url="https://example.com",
            email="test@example.com",
            slug="test-name",
            ip_address="127.0.0.1",
            big_integer=9999999999,
            positive_integer=123,
            small_integer=12,
            duration=timedelta(days=1),
            json_data={"key": "value"}
        )

    def test_${APP_NAME}_creation(self):
        self.assertIsInstance(self.${APP_NAME}_instance, $SINGULAR_CAPITALIZED)
        self.assertEqual(self.${APP_NAME}_instance.__str__(), self.${APP_NAME}_instance.name)
EOL

# Ensure settings file is saved and changes are applied
sleep 2

# Make migrations and migrate
python manage.py makemigrations "$PLURAL_UNDERSCORED"
python manage.py migrate

echo "App '$PLURAL_UNDERSCORED' has been created and configured successfully."
