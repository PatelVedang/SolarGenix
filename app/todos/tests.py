from django.test import TestCase
from datetime import timedelta
from .models import Todo

class TodoModelTests(TestCase):

    def setUp(self):
        self.todos_instance = Todo.objects.create(
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

    def test_todos_creation(self):
        self.assertIsInstance(self.todos_instance, Todo)
        self.assertEqual(self.todos_instance.__str__(), self.todos_instance.name)
