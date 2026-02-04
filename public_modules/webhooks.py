import stripe
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from .models import Donation
from .utils import generate_receipt_image

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        stripe_api_key = settings.STRIPE_SECRET_KEY
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)

        if not endpoint_secret:
             # If no secret is set, we can't verify the signature properly in prod, 
             # but for now we might risk it or just fail. 
             # Let's log error but proceed if in debug/dev if we want (unsafe), 
             # or better: fail and tell user to set it.
             # For this implementation, we will assume it is set or fail.
             return HttpResponse("Webhook secret not configured", status=400)

        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            stripe_payment_intent_id = payment_intent['id']

            try:
                donation = Donation.objects.get(stripe_payment_intent_id=stripe_payment_intent_id)
                
                # Check if already completed to avoid duplicate work
                if donation.status != 'COMPLETED':
                    donation.status = 'COMPLETED'
                    # Generate receipt
                    try:
                         generate_receipt_image(donation)
                    except Exception as e:
                         print(f"Error generating receipt: {e}")
                         # Continue to save status at least
                    
                    donation.save()
                    print(f"Donation {donation.id} completed successfully.")
                else:
                    print(f"Donation {donation.id} was already completed.")

            except Donation.DoesNotExist:
                print(f"Donation for PaymentIntent {stripe_payment_intent_id} not found.")
                return HttpResponse(status=404)

        return HttpResponse(status=200)
