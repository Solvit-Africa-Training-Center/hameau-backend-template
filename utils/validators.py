import re
from django.utils import timezone
from rest_framework import serializers
from decimal import Decimal

def validate_rwanda_phone(value):
    """
    Validates Rwanda phone number format.
    Supports formats: 07..., +2507..., or 2507... followed by 8 digits.
    """
    if value:
        pattern = r'^(07|\+2507|2507)[2389]\d{7}$'
        if not re.match(pattern, str(value)):
            raise serializers.ValidationError("Invalid phone number format. Please use 07..., +2507..., or 2507...")
    return value

def validate_national_id_format(value):
    """
    Validates that National ID is exactly 16 digits.
    """
    if value:
        if not value.isdigit() or len(value) != 16:
            raise serializers.ValidationError("National ID must be exactly 16 digits.")
    return value

def validate_not_future_date(value, field_name="Date"):
    """
    Ensures a date is not in the future.
    """
    if value and value > timezone.now().date():
        raise serializers.ValidationError(f"{field_name} cannot be in the future.")
    return value

def validate_not_negative(value, field_name="Value"):
    """
    Ensures a value is not negative.
    """
    if value is not None and value < 0:
        raise serializers.ValidationError(f"{field_name} cannot be negative.")
    return value
