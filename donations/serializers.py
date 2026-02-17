from rest_framework import serializers
from .models import Donor, Donation, SponsorEmailLog
from programs.serializers.residentials_serializers import ChildReadSerializer

class DonorSerializer(serializers.ModelSerializer):
    """
    Serializer for Donor management. 
    Handles basic contact info and type classification.
    """
    class Meta:
        model = Donor
        fields = ["id", "fullname", "email", "phone", "address", "donor_type", "created_on"]
        read_only_fields = ["id", "created_on"]


class DonationSerializer(serializers.ModelSerializer):
    """
    Serializer for Contributions. 
    Includes business logic for three donation types (General, Child, Family)
    and validates requirements for recurring payments.
    """
    child_info = ChildReadSerializer(source="child", read_only=True)
    donor_name = serializers.CharField(source="donor.fullname", read_only=True)
    family_name = serializers.CharField(source="family.name", read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "donor",
            "donor_name",
            "donation_type",
            "child",
            "child_info",
            "family",
            "family_name",
            "amount",
            "currency",
            "donation_purpose",
            "payment_method",
            "is_recurring",
            "recurring_interval",
            "next_deduction_date",
            "donation_date",
            "receipt_image",
            "notes",
            "created_on",
        ]
        read_only_fields = ["id", "donation_date", "created_on", "next_deduction_date"]

    def validate(self, attrs):
        """
        Business Logic:
        1. Ensure child is selected for RESIDENTIAL_CHILD donation.
        2. Ensure family is selected for IFASHE_FAMILY donation.
        3. Clear inappropriate foreign keys based on donation_type.
        4. Validate recurring interval for periodic payments.
        """
        donation_type = attrs.get("donation_type")
        child = attrs.get("child")
        family = attrs.get("family")
        is_recurring = attrs.get("is_recurring", False)
        recurring_interval = attrs.get("recurring_interval")

        # 1. Periodic Payment Validation
        if is_recurring and not recurring_interval:
            raise serializers.ValidationError(
                {"recurring_interval": "Recurring interval is required if is_recurring is set."}
            )

        # 2. Donation Type Specific Logic
        if donation_type == Donation.RESIDENTIAL_CHILD:
            if not child:
                raise serializers.ValidationError(
                    {"child": "A child must be selected for Residential Child donations."}
                )
            attrs["family"] = None
        
        elif donation_type == Donation.IFASHE_FAMILY:
            if not family:
                raise serializers.ValidationError(
                    {"family": "A family must be selected for Ifashe-Tugufashe Family donations."}
                )
            attrs["child"] = None
            
        elif donation_type == Donation.GENERAL:
            attrs["child"] = None
            attrs["family"] = None

        return attrs

    def create(self, validated_data):
        """
        Handles creation of donation record.
        Integration with IremboPay occurs here to generate a payment session if selected.
        Also calculates the next deduction date for recurring payments.
        """
        is_recurring = validated_data.get("is_recurring", False)
        payment_method = validated_data.get("payment_method")
        
        # 1. Handle Recurring Logic
        if is_recurring:
            from .services import calculate_next_deduction_date
            from django.utils import timezone
            now = timezone.now().date()
            interval = validated_data.get("recurring_interval")
            validated_data["next_deduction_date"] = calculate_next_deduction_date(now, interval)

        # 2. IremboPay Integration Pattern
        if payment_method == Donation.IREMBOPAY:
            # Here we would typically call the IremboPay API to initiate a transaction
            # and get a redirect URL or session token.
            # Example Placeholder:
            # irembo_session = irembo_service.create_session(
            #     amount=validated_data['amount'],
            #     donor_email=validated_data['donor'].email if validated_data.get('donor') else None,
            #     is_recurring=is_recurring
            # )
            # validated_data['notes'] = f"Irembo Session ID: {irembo_session.id}"
            pass

        return super().create(validated_data)


class SponsorEmailLogSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for tracking report delivery history.
    """
    donor_name = serializers.CharField(source="donor.fullname", read_only=True)
    child_name = serializers.CharField(source="child.full_name", read_only=True)

    class Meta:
        model = SponsorEmailLog
        fields = [
            "id",
            "donor",
            "donor_name",
            "child",
            "child_name",
            "sent_at",
            "month",
            "year",
            "status",
            "error_message"
        ]
