from rest_framework import serializers
from .models import Donor, Donation

class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = '__all__'
class DonationSerializer(serializers.ModelSerializer):
    donor = DonorSerializer(read_only=True)
    donor_id = serializers.PrimaryKeyRelatedField(
        queryset=Donor.objects.all(), source='donor', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Donation
        fields = [
            'id', 'donor', 'donor_id', 'amount', 'currency', 'donation_purpose', 
            'payment_method', 'donation_date', 'receipt_image', 'notes', 
            'status', 'stripe_payment_intent_id'
        ]
        read_only_fields = ['status', 'stripe_payment_intent_id', 'donation_date']
       
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Donation amount must be greater than zero")
        return value

class CreatePaymentIntentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default='usd')
    donor_id = serializers.CharField(required=False, allow_null=True)
    donation_purpose = serializers.CharField(required=False, allow_blank=True)
    
    # New fields for inline donor creation
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    
