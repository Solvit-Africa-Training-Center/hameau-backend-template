from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from public_modules.models import Donation
import stripe
from django.conf import settings

class PaymentIntentTest(TestCase):
    def test_create_payment_intent(self):
        client = Client()
        url = reverse('create-payment-intent')
        data = {
            'amount': '50.00',
            'currency': 'usd',
            'donation_purpose': 'Test Donation'
        }

        # Mock stripe.PaymentIntent.create
        with patch('stripe.PaymentIntent.create') as mock_create:
            mock_create.return_value = {
                'id': 'pi_test_123',
                'client_secret': 'pi_test_123_secret_456'
            }

            response = client.post(url, data, content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['clientSecret'], 'pi_test_123_secret_456')
            
            # Verify Donation was created
            donation = Donation.objects.get(stripe_payment_intent_id='pi_test_123')
            self.assertEqual(donation.amount, 50.00)
            self.assertEqual(donation.status, 'PENDING')

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_success(self, mock_construct_event):
        # Create a pending donation
        donation = Donation.objects.create(
            amount=100.00,
            currency='usd',
            status='PENDING',
            stripe_payment_intent_id='pi_test_webhook'
        )

        url = reverse('stripe-webhook')
        
        # Mock the event data
        mock_event = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_webhook'
                }
            }
        }
        mock_construct_event.return_value = mock_event
        
        # We need to set a dummy secret in settings for the view to proceed or mock settings
        with self.settings(STRIPE_WEBHOOK_SECRET='whsec_test'):
            response = self.client.post(
                url, 
                data='payload', 
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test_signature'
            )
            
            self.assertEqual(response.status_code, 200)
            
            # Verify Donation was updated
            donation.refresh_from_db()
            self.assertEqual(donation.status, 'COMPLETED')
            self.assertTrue(donation.receipt_image) 
            # Note: Checking if file exists might fail if using dummy storage in tests without cleanup, 
            # but assertTrue check if field is not null/empty.

    @patch('stripe.Webhook.construct_event')
    def test_stripe_webhook_invalid_signature(self, mock_construct_event):
        url = reverse('stripe-webhook')
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError("Invalid signature", "sig_header")
        
        with self.settings(STRIPE_WEBHOOK_SECRET='whsec_test'):
            response = self.client.post(
                url, 
                data='payload', 
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='invalid_signature'
            )
            self.assertEqual(response.status_code, 400)
