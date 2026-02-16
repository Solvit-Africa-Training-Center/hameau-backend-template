from rest_framework import serializers
from .models import Donor, Donation, SponsorEmailLog
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

    class Meta:
        model = Donation
        fields = [
            "id",
            "donor",
            "donor_details",
            "child",
            "child_details",
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


class SponsorEmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsorEmailLog
        fields = "__all__"
