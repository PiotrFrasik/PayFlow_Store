from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, MagicMock

class StripeWebhookAPITest(APITestCase):
    def setUp(self):
        self.url_webhook = reverse("stripe-webhook")

    def test_webhook_without_signature_returns_400(self):
        """Return 400 Bad Request when the Stripe signature header is missing."""
        response = self.client.post(self.url_webhook, data={}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('orders.views.stripe.Webhook.construct_event')
    def test_webhook_with_wrong_payload_returns_400(self, MockConstructEvent):
        """Return 400 Bad Request when the payload is invalid (ValueError)."""
        MockConstructEvent.side_effect = ValueError("Invalid payload")
        response = self.client.post(self.url_webhook, data={}, format="json", HTTP_STRIPE_SIGNATURE="fake_signature")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('orders.views.stripe.Webhook.construct_event')
    def test_webhook_with_bad_signature_returns_400(self, MockConstructEvent):
        """Return 400 Bad Request when the Stripe signature is invalid (SignatureVerificationError)."""
        import stripe
        MockConstructEvent.side_effect = stripe.error.SignatureVerificationError("Invalid sig", "sig")
        response = self.client.post(self.url_webhook, data={}, format="json", HTTP_STRIPE_SIGNATURE="bad_signature")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('orders.views.stripe.Webhook.construct_event')
    def test_webhook_with_not_existing_order_returns_404(self, MockConstructEvent):
        """Return 404 Not Found if checkout completes for a non-existent order."""
        mock_session = MagicMock()
        mock_session.client_reference_id = 9999

        MockConstructEvent.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': mock_session
            }
        }
        response = self.client.post(self.url_webhook, data={}, format="json", HTTP_STRIPE_SIGNATURE="valid_signature")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
