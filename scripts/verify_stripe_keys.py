import os
import sys
import django
import stripe

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.conf import settings

def verify_stripe_keys():
    print("Verifying Stripe Configuration...")
    
    # Check if keys are loaded
    pub_key = settings.STRIPE_PUBLISHABLE_KEY
    sec_key = settings.STRIPE_SECRET_KEY
    
    if not pub_key:
        print("ERROR: STRIPE_PUBLISHABLE_KEY is missing in settings.")
        return
    if not sec_key:
        print("ERROR: STRIPE_SECRET_KEY is missing in settings.")
        return
        
    print(f"Publishable Key: {pub_key[:8]}...{pub_key[-4:]}")
    print(f"Secret Key:      {sec_key[:8]}...{sec_key[-4:]}")

    # Set the key
    stripe.api_key = sec_key

    try:
        print("\nAttempting to connect to Stripe API...")
        # Make a simple API call to verify credentials
        balance = stripe.Balance.retrieve()
        print("SUCCESS: Successfully connected to Stripe!")
        print(f"Available Balance: {balance['available'][0]['amount']} {balance['available'][0]['currency'].upper()}")
        print(f"Live Mode: {balance['livemode']}")
        
        if not balance['livemode']:
             print("Configuration is correctly set to TEST mode.")
        else:
             print("WARNING: Configuration is set to LIVE mode.")

    except stripe.error.AuthenticationError:
        print("ERROR: Authentication failed. Please check your API keys.")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    verify_stripe_keys()
