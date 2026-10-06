from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth.models import User


from orders.models import Order, OrderItem
from products.models import Product

class OrderAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.url = reverse("cart")

        self.out_of_stock_product = Product.objects.create(
                name = "Produkt 2",
                price=10.00,
                stock_status=0,
                is_digital=False
        )

        self.url_create = reverse("create-order")

        self.create_product = Product.objects.create(
                name = "Produkt 4",
                price=15.00,
                stock_status=2,
                is_digital=False
        )

    # --- CREATE ORDER ---

    def test_create_order_unauthenticated_returns_401(self):
        """Return 401 Unauthorized when an unauthenticated user tries to create an order."""
        response = self.client.post(self.url_create, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('orders.views.RedisCart')
    def test_create_order_with_empty_cart_returns_400(self, MockRedisCart):
        """Return 400 Bad Request when trying to create an order with an empty cart."""
        mock_cart= MockRedisCart.return_value
        mock_cart.get_items.return_value = {}
        self.client.force_authenticate(user=self.user) 
        response = self.client.post(self.url_create, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('orders.views.RedisCart')
    def test_create_order_with_out_of_stock_product_returns_400(self, MockRedisCart):
        """Return 400 Bad Request when trying to create an order containing an out-of-stock physical product."""
        mock_cart= MockRedisCart.return_value
        mock_cart.get_items.return_value = {self.out_of_stock_product.id: 1}
        self.client.force_authenticate(user=self.user) 
        response = self.client.post(self.url_create, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('orders.views.RedisCart')
    def test_create_order_not_existing_product_in_cart_returns_404(self, MockRedisCart):
        """Return 404 Not Found when trying to create an order for a product that does not exist in the database."""
        mock_cart= MockRedisCart.return_value
        mock_cart.get_items.return_value = {'5': 1}
        self.client.force_authenticate(user=self.user) 

        response = self.client.post(self.url_create, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('orders.views.stripe.checkout.Session.create')
    def test_create_order_returns_201(self, MockStripeSessionCreate):
        """Return 201 Created and pending status when successfully creating an order (mocks Stripe Session)."""
        mock_session = MockStripeSessionCreate.return_value
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/fake"
        
        self.client.force_authenticate(user=self.user) 
        response = self.client.post(self.url, data={'product_id': self.create_product.id}, format="json")

        response = self.client.post(self.url_create, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['order']['status'], Order.OrderStatus.PENDING)



