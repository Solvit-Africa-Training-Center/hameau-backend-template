from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
import stripe


from .models import Donor, Donation
from .serializers import DonorSerializer, DonationSerializer, CreatePaymentIntentSerializer
from rest_framework.permissions import AllowAny, IsAdminUser

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreatePaymentIntentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs): 
        serializer = CreatePaymentIntentSerializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            currency = serializer.validated_data['currency']
            donation_purpose = serializer.validated_data.get('donation_purpose', '')

    # donor_id = serializer.validated_data.get('donor_id') # Optional handling

            try:
                # Create a PaymentIntent with the order amount and currency
                intent = stripe.PaymentIntent.create( 
                    amount=int(amount * 100),  # Convert to cents
                    currency=currency,
                    automatic_payment_methods={ 
                        'enabled': True,
                    },
                    metadata={
                        'donation_purpose': donation_purpose,
                        # 'donor_id': donor_id
                    }
                )

                # Here is created a pending Donation record in the database
                donation = Donation.objects.create(
                    amount=amount,
                    currency=currency,
                    donation_purpose=donation_purpose,
                    status='PENDING',
                    stripe_payment_intent_id=intent['id'],
                    # donor=... # Here is where i want to link donor here if provided
                    donor_id = serializer.validated_data.get('donor_id') # Optional            handling
                )

                return Response({
                    'clientSecret': intent['client_secret'],
                    'donationId': donation.id
                })
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer
    permission_classes = [permissions.AllowAny]

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]
