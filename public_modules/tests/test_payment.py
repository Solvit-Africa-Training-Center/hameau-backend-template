from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from public_modules.models import Donation

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
