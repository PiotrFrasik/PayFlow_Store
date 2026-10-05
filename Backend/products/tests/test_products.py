from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

from products.models import Product

class ProductListAPITests(APITestCase):
    def setUp(self):

        self.product1 = Product.objects.create(
            name = "Produkt 1",
            price=10.00,
            stock_status=5,
            is_digital=False
        )

        self.product2 = Product.objects.create(
            name="Produkt Cyfrowy",
            price=5.00,
            is_digital=True
        )

        self.user = User.objects.create_user(username="testuser", password="testpassword")

        self.url = reverse("products")

        self.url_id_product1 = reverse("product-detail", kwargs={"pk": self.product1.id})

        self.product3 = {
            "name": "Produkt 3",
            "price": 12.00,
            "stock_status": 2,
            "is_digital": False
        }

    def test_get_product_list_as_unauthenticated_returns_200(self):
        """Ensure unauthenticated users can retrieve the product list."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_product_list_as_authenticated_returns_200(self):
        """Ensure authenticated users can retrieve the product list."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_product_by_existing_id_returns_200(self):
        """Ensure users can retrieve a specific product by its ID."""
        response = self.client.get(self.url_id_product1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_by_non_existing_id_returns_404(self):
        """Ensure a 404 is returned when requesting a non-existent product."""
        non_existing_url = reverse("product-detail", kwargs={"pk": 9999})
        response = self.client.get(non_existing_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_product_returns_401(self):
        """Ensure unauthenticated users receive 401 Unauthorized on POST."""
        response = self.client.post(self.url, self.product3, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)