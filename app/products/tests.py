# import os,json, tempfile
# from PIL import Image
# from django.test import TestCase
# from django.urls import reverse
# from datetime import date
# from datetime import timedelta
# from rest_framework.test import APITestCase, APIClient
# from django.core.files.uploadedfile import SimpleUploadedFile
# from rest_framework import status
# from .models import Product
# from auth_api.models import User


# class ProductModelTests(TestCase):

#     # def setUp(self):
#     #     self.products_instance = Product.objects.create(
#     #         name="Test Name",
#     #         description="Test description",
#     #         price=9.99,
#     #         inventory=100,
#     #         available=True,
#     #         published_date="2024-01-01",
#     #         rating=4.5,
#     #         url="https://example.com",
#     #         email="test@example.com",
#     #         slug="test-name",
#     #         ip_address="127.0.0.1",
#     #         big_integer=9999999999,
#     #         positive_integer=123,
#     #         small_integer=12,
#     #         duration=timedelta(days=1),
#     #         json_data={"key": "value"}
#     #     )

#     # def test_products_creation(self):
#     #     self.assertIsInstance(self.products_instance, Product)
#     #     self.assertEqual(self.products_instance.__str__(), self.products_instance.name)
#     def setUp(self):
#         # Create a user and set the password
#         self.user = User.objects.create_superuser(
#             email='testuser@example.com',
#             name='Test User',
#             password='testpass123',
#             tc=True,
#         )
#         self.user.is_active = True
#         self.user.save()

#         # Authenticate the user and obtain the token
#         self.client = APIClient()
#         login_response = self.client.post(reverse('login'), {
#             'email': 'testuser@example.com',
#             'password': 'testpass123'
#         }, format='json')

#         # Extract access token
#         self.access_token = login_response.data['access']
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

#         # Create a temporary image for testing
#         self.image = self.generate_test_image()
#         # Create a temporary file for testing
#         self.file, self.file_path = self.generate_test_file()

#         # Set up a products instance
#         self.products = Product.objects.create(
#             name='Test Name',
#             description='Test description',
#             price=9.99,
#             inventory=10,
#             published_date=date(2024, 7, 1),
#             rating=4.5,
#             url='http://example.com',
#             email='info@example.com',
#             slug='test-products',
#             ip_address='127.0.0.1',
#             big_integer=9999999999,
#             positive_integer=10,
#             small_integer=5,
#             duration='01:00:00',
#             json_data={"key": "value"},
#             image=self.image,
#             file=self.file,
#         )

#     def generate_test_image(self):
#         # Create a temporary image file
#         with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image:
#             image = Image.new("RGB", (100, 100), color=(255, 0, 0))
#             image.save(temp_image, format='PNG')
#             temp_image.seek(0)
#             return SimpleUploadedFile(temp_image.name, temp_image.read(), content_type='image/png')

#     def generate_test_file(self):
#         # Create a temporary file
#         file_content = b'This is a test file.'
#         temp_file = tempfile.NamedTemporaryFile(delete=False)
#         temp_file.write(file_content)
#         temp_file.flush()
#         temp_file.seek(0)  # Go back to the start of the file for reading
#         return SimpleUploadedFile(temp_file.name, temp_file.read(), content_type='text/plain'), temp_file.name

#     def test_create_products_authentication(self):
#         url = reverse('products-list')  # Ensure this URL name matches your URL pattern

#         # Flatten or serialize JSON data
#         json_data_str = json.dumps({"key": "new value"})

#         sample_image = self.generate_test_image()
#         test_file = self.generate_test_file()
#         data = {
#             "name": "New products",
#             "description": "New description",
#             "price": 10.99,
#             "inventory": 15,
#             "published_date": "2024-07-02",
#             "rating": 4.7,
#             "url": "http://example.com/new",
#             "email": "new@example.com",
#             "slug": "new-products",
#             "ip_address": "127.0.0.1",
#             "big_integer": 8888888888,
#             "positive_integer": 15,
#             "small_integer": 7,
#             "duration": "02:00:00",
#             "json_data": json_data_str,  # Pass JSON data as string
#             "image": sample_image,  # Add image here
#             "file": test_file,  # Add file here
#         }

#         response = self.client.post(url, data, format='multipart')
#         data = response.data.get("data", None)
#         products_id = data.get("id") if data else None
#         if products_id:
#             products_instance =Product.objects.get(id=products_id)
#             if products_instance.image:
#                 products_instance.image.delete(save=False)
#             if products_instance.file:
#                 products_instance.file.delete(save=False)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_create_products_without_authentication(self):
#         # Authenticate the user and obtain the token
#         self.client = APIClient()
#         self.client.credentials()
#         url = reverse('products-list')  # Ensure this URL name matches your URL pattern

#         # Flatten or serialize JSON data
#         json_data_str = json.dumps({"key": "new value"})

#         sample_image = self.generate_test_image()
#         test_file = self.generate_test_file()
#         data = {
#             "name": "New Product",
#             "description": "New description",
#             "price": 10.99,
#             "inventory": 15,
#             "published_date": "2024-07-02",
#             "rating": 4.7,
#             "url": "http://example.com/new",
#             "email": "new@example.com",
#             "slug": "new-products",
#             "ip_address": "127.0.0.1",
#             "big_integer": 8888888888,
#             "positive_integer": 15,
#             "small_integer": 7,
#             "duration": "02:00:00",
#             "json_data": json_data_str,  # Pass JSON data as string
#             "image": sample_image,  # Add image here
#             "file": test_file,  # Add file here
#         }

#         response = self.client.post(url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_create_products_validation(self):
#         # Authenticate the user and obtain the token
#         url = reverse('products-list')  # Ensure this URL name matches your URL pattern

#         # Flatten or serialize JSON data
#         json_data_str = json.dumps({"key": "new value"})

#         sample_image = self.generate_test_image()
#         test_file = self.generate_test_file()
#         data = {
#             "name": 123, # pass int value instead of str
#             "description": "New description",
#             "price": 10.99,
#             "inventory": 15,
#             "published_date": "2024-07-02",
#             "rating": '4.7',
#             "url": "example.com/new", #pass wrong field value
#             "email": "new",
#             "slug": "new-products",
#             "ip_address": "127.0.0.1",
#             "big_integer": 8888888888,
#             "positive_integer": 15,
#             "small_integer": 7,
#             "duration": "02:00:00",
#             "json_data": json_data_str,  # Pass JSON data as string
#             "image": sample_image,  # Add image here
#             "file": test_file,  # Add file here
#         }

#         response = self.client.post(url, data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_read_products_authentication(self):
#         url = reverse('products-detail', args=[self.products.id])  # Ensure this URL name matches your URL pattern

#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['data']['name'], self.products.name)

#     def test_read_products_without_authentication(self):
#         # Authenticate the user and obtain the token
#         self.client = APIClient()
#         self.client.credentials()

#         url = reverse('products-detail', args=[self.products.id])  # Ensure this URL name matches your URL pattern

#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         # self.assertEqual(response.data['data']['name'], self.products.name)

#     def test_read_products_with_not_exists_id(self):
#         url = reverse('products-detail', args=[1231465])  # Ensure this URL name matches your URL pattern

#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
#         # self.assertEqual(response.data['data']['name'], self.products.name)

#     def test_update_products_authentication(self):
#         url = reverse('products-detail', args=[self.products.id])  # Ensure this URL name matches your URL pattern

#         updated_data = {
#             "name": "Updated products",
#             "description": "Updated description",
#             "price": 11.99,
#             "inventory": 20,
#             "published_date": "2024-07-03",
#             "rating": 4.9,
#             "url": "http://example.com/updated",
#             "email": "updated@example.com",
#             "slug": "updated-products",
#             "ip_address": "127.0.0.2",
#             "big_integer": 7777777777,
#             "positive_integer": 20,
#             "small_integer": 10,
#             "duration": "03:00:00",
#             "json_data": json.dumps({"key": "updated value"}),  # Pass JSON data as string
#             "image": self.generate_test_image(),  # Add updated image here
#             "file": self.generate_test_file(),  # Add updated file here
#         }

#         response = self.client.patch(url, updated_data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['data']['name'], updated_data['name'])

#     def test_update_products_without_authentication(self):
#         # Authenticate the user and obtain the token
#         self.client = APIClient()
#         self.client.credentials()

#         url = reverse('products-detail', args=[self.products.id])  # Ensure this URL name matches your URL pattern

#         updated_data = {
#             "name": "Updated Product",
#             "description": "Updated description",
#             "price": 11.99,
#             "inventory": 20,
#             "published_date": "2024-07-03",
#             "rating": 4.9,
#             "url": "http://example.com/updated",
#             "email": "updated@example.com",
#             "slug": "updated-products",
#             "ip_address": "127.0.0.2",
#             "big_integer": 7777777777,
#             "positive_integer": 20,
#             "small_integer": 10,
#             "duration": "03:00:00",
#             "json_data": json.dumps({"key": "updated value"}),  # Pass JSON data as string
#             "image": self.generate_test_image(),  # Add updated image here
#             "file": self.generate_test_file(),  # Add updated file here
#         }

#         response = self.client.patch(url, updated_data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_update_products_validation(self):
#         url = reverse('products-detail', args=[self.products.id])  # Ensure this URL name matches your URL pattern

#         updated_data = {
#             "url":"worng value"
#         }

#         response = self.client.patch(url, updated_data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_update_products_with_not_exists_id(self):
#         url = reverse('products-detail', args=[0])  # Ensure this URL name matches your URL pattern

#         updated_data = {
#             "name": "Updated Product",
#             "description": "Updated description",
#             "price": 11.99,
#             "inventory": 20,
#             "published_date": "2024-07-03",
#             "rating": 4.9,
#             "url": "http://example.com/updated",
#             "email": "updated@example.com",
#             "slug": "updated-products",
#             "ip_address": "127.0.0.2",
#             "big_integer": 7777777777,
#             "positive_integer": 20,
#             "small_integer": 10,
#             "duration": "03:00:00",
#             "json_data": json.dumps({"key": "updated value"}),  # Pass JSON data as string
#             "image": self.generate_test_image(),  # Add updated image here
#             "file": self.generate_test_file(),  # Add updated file here
#         }

#         response = self.client.patch(url, updated_data, format='multipart')
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_partial_update_products_authenticated(self):
#         url = reverse('products-detail', args=[self.products.id])  # Ensure this URL name matches your URL pattern

#         updated_data = {
#             "name": "Partially Updated Product"
#         }

#         response = self.client.patch(url, updated_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['data']['name'], updated_data['name'])

#     def test_partial_update_products_without_authentication(self):
#         # Authenticate the user and obtain the token
#         self.client = APIClient()
#         self.client.credentials()

#         url = reverse('products-detail', args=[self.products.id])  # Ensure this URL name matches your URL pattern

#         updated_data = {
#             "name": "Partially Updated Product"
#         }

#         response = self.client.patch(url, updated_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_partial_update_products_validation(self):
#         url = reverse('products-detail', args=[self.products.id])  # Ensure this URL name matches your URL pattern

#         updated_data = {
#             "url": "Partially Updated Product"
#         }

#         response = self.client.patch(url, updated_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_delete_products_authenticated(self):
#         url = reverse('products-detail', args=[self.products.id])  # Ensure this URL name matches your URL pattern

#         response = self.client.delete(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Product.objects.filter(id=self.products.id).exists())

#     def test_delete_products_without_authentication(self):
#         # Authenticate the user and obtain the token
#         self.client = APIClient()
#         self.client.credentials()

#         url = reverse('products-detail', args=[self.products.id])  # Ensure this URL name matches your URL pattern

#         response = self.client.delete(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_delete_products_not_exists_id(self):
#         url = reverse('products-detail', args=[0])  # Ensure this URL name matches your URL pattern

#         response = self.client.delete(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_list_all_products(self):
#         self.access_token = ''
#         url = reverse('products-list')
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def tearDown(self):
#         # Delete temporary files after the test
#         self.products.image.delete(save=False)  # Delete the image file if it was saved to media
#         self.products.file.delete(save=False)   # Delete the file if it was saved to media
#         if os.path.exists(self.file_path):
#             os.remove(self.file_path)
