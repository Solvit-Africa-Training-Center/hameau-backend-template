from rest_framework import serializers
from django.db import transaction
from .models import Donor, Donation, SponsorEmailLog
from programs.models.residentials_models import Child
from programs.models.ifashe_models import Family
from programs.serializers.residentials_serializers import ChildReadSerializer

class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = [
            "id",
            "fullname",
            "email",
            "phone",
            "address",
            "donor_type",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


class DonationSerializer(serializers.ModelSerializer):
    donor_details = DonorSerializer(source="donor", read_only=True)
    child_details = ChildReadSerializer(source="child", read_only=True)
    family_name = serializers.CharField(source="family.family_name", read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "donor",
            "donor_details",
            "donation_type",
            "child",
            "child_details",
            "family",
            "family_name",
            "amount",
            "currency",
            "donation_purpose",
            "payment_method",
            "donation_date",
            "receipt_image",
            "notes",
            "created_on",
        ]
        read_only_fields = ["id", "donation_date", "created_on"]

    def validate(self, attrs):
        donation_type = attrs.get("donation_type")
        child = attrs.get("child")
        family = attrs.get("family")

        if donation_type == Donation.RESIDENTIAL_CHILD:
            if not child:
                raise serializers.ValidationError(
                    {"child": "A child must be selected for Residential Child donations."}
                )
            # Ensure family is not set for residential child
            attrs["family"] = None
        
        elif donation_type == Donation.IFASHE_FAMILY:
            if not family:
                raise serializers.ValidationError(
                    {"family": "A family must be selected for Ifashe-Tugufashe Family donations."}
                )
            # Ensure child is not set for family donation
            attrs["child"] = None
            
        elif donation_type == Donation.GENERAL:
            # For general donations, both child and family should be null
            attrs["child"] = None
            attrs["family"] = None

        return attrs

    def create(self, validated_data):
        """
        Business logic for donation creation is handled here.
        This ensures that even if API users send extraneous data, 
        the data integrity is maintained based on donation_type.
        """
        return super().create(validated_data)


class SponsorEmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsorEmailLog
        fields = "__all__"
