from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.contrib.auth.models import User

from products.models import Product

class CartAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.url = reverse("cart")

        self.in_stock_product = Product.objects.create(
                name = "Produkt 1",
                price=10.00,
                stock_status=5,
                is_digital=False
        )

        self.out_of_stock_product = Product.objects.create(
                name = "Produkt 2",
                price=10.00,
                stock_status=0,
                is_digital=False
        )

        self.delete_product = Product.objects.create(
                name = "Produkt 3",
                price=13.00,
                stock_status=2,
                is_digital=False
        )

    # --- GET CART ---

    @patch('orders.views.RedisCart')
    def test_get_cart_filled_returns_200(self, MockRedisCart):
        """Return 200 OK and cart items when cart is not empty."""
        mock_cart= MockRedisCart.return_value
        mock_cart.get_items.return_value = {'1': 2, '5': 3}

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'1': 2, '5': 3})

    @patch('orders.views.RedisCart')
    def test_get_cart_empty_returns_200(self, MockRedisCart):
        """Return 200 OK and an empty dict when cart is empty."""
        mock_cart= MockRedisCart.return_value
        mock_cart.get_items.return_value = {}
  
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_get_cart_unauthenticated_returns_401(self):
        """Return 401 Unauthorized when user is not logged in."""
        self.client.force_authenticate() 
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    # --- ADD PRODUCT TO CART ---
    def test_add_product_to_cart_without_id_returns_400(self):
        """Return 400 Bad Request when product_id is missing."""
        self.client.force_authenticate(user=self.user) 
        response = self.client.post(self.url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_product_to_cart_not_existing_id_returns_404(self):
        """Return 404 Not Found when product does not exist."""
        self.client.force_authenticate(user=self.user) 
        response = self.client.post(self.url, data={'product_id': 9999}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_out_of_stock_product_to_cart_returns_400(self):
        """Return 400 Bad Request when physical product is out of stock."""
        self.client.force_authenticate(user=self.user) 
        response = self.client.post(self.url, data={'product_id': self.out_of_stock_product.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_in_stock_product_to_cart_returns_200(self):
        """Return 200 OK when product is successfully added to cart."""
        self.client.force_authenticate(user=self.user) 
        response = self.client.post(self.url, data={'product_id': self.in_stock_product.id}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- DELETE PRODUCT TO CART ---

    def test_delete_product_from_cart_without_id_returns_400(self):
        """Return 400 Bad Request when product_id is missing during deletion."""
        self.client.force_authenticate(user=self.user) 
        response = self.client.delete(self.url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_product_from_cart_returns_200(self):
        """Test full cycle: add product, remove it, and check if cart is empty."""
        # 1. Add product to cart
        self.client.force_authenticate(user=self.user) 
        response = self.client.post(self.url, data={'product_id': self.delete_product.id}, format="json")

        # 2. Remove product from cart
        self.client.force_authenticate(user=self.user) 
        response = self.client.delete(self.url, data={'product_id': self.delete_product.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. Verify that the cart is indeed empty
        self.client.force_authenticate(user=self.user) 
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
    
    def test_delete_not_exisiting_product_in_cart_returns_404(self):
        """Return 404 Not Found when deleting a non-existent product."""
        self.client.force_authenticate(user=self.user) 
        response = self.client.delete(self.url, data={'product_id': 1}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
