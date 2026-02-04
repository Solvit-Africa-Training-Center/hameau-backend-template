from django.utils import timezone
from rest_framework import serializers
from programs.models import Family, Parent, SponsoredChild
import re
from utils.validators import (
    validate_rwanda_phone, 
    validate_national_id_format, 
    validate_not_future_date, 
    validate_not_negative
)


class IfasheParentSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    family_id = serializers.PrimaryKeyRelatedField(
        source='family',
        queryset=Family.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Parent
        fields = [
            'id', 'family_id', 'first_name', 'last_name', 'full_name',
            'gender', 'relationship', 'phone', 'address', 'national_id',
            'date_of_birth', 'education_level', 'marital_status',
            'previous_employment', 'monthly_income', 'national_id_doc'
        ]

    def validate_national_id(self, value):
        return validate_national_id_format(value)

    def validate_phone(self, value):
        return validate_rwanda_phone(value)

    def validate_date_of_birth(self, value):
        return validate_not_future_date(value, "Date of birth")

    def validate_monthly_income(self, value):
        return validate_not_negative(value, "Monthly income")


class IfasheChildSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    family_name = serializers.ReadOnlyField(source='family.family_name')
    family_id = serializers.PrimaryKeyRelatedField(
        source='family',
        queryset=Family.objects.all(),
        required=False
    )

    class Meta:
        model = SponsoredChild
        fields = [
            'id', 'family_id', 'family_name', 'first_name', 'last_name', 
            'full_name', 'date_of_birth', 'gender', 'school_name', 
            'school_level', 'health_conditions', 'support_status', 
            'profile_image', 'birth_certificate', 'school_report'
        ]
        extra_kwargs = {
            'gender': {'required': True},
            'school_name': {'required': True},
            'school_level': {'required': True},
        }

    def validate_date_of_birth(self, value):
        return validate_not_future_date(value, "Date of birth")


class IfasheFamilySerializer(serializers.ModelSerializer):
    family_id = serializers.ReadOnlyField(source='id')
    parents = IfasheParentSerializer(many=True, required=False)
    children = IfasheChildSerializer(many=True, required=False)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = [
            'id', 'family_id', 'family_name', 'address', 'province',
            'district', 'sector', 'cell', 'village',
            'vulnerability_level', 'housing_condition', 'family_members',
            'social_worker_assessment', 'proof_of_residence',
            'parents', 'children', 'children_count'
        ]
        extra_kwargs = {
            'family_id': {'read_only': True}
        }

    def validate_family_members(self, value):
        # Using 1 as minimum as per previous logic
        if value is not None and value < 1:
            raise serializers.ValidationError("Family members count must be at least 1.")
        return value

    def get_children_count(self, obj):
        return obj.children.count()

    def create(self, validated_data):
        parents_data = validated_data.pop('parents', [])
        children_data = validated_data.pop('children', [])
        family = Family.objects.create(**validated_data)
        
        for parent_data in parents_data:
            parent_data.pop('family', None)  # Avoid duplicate family argument
            Parent.objects.create(family=family, **parent_data)
            
        for child_data in children_data:
            child_data.pop('family', None)   # Avoid duplicate family argument
            SponsoredChild.objects.create(family=family, **child_data)
            
        return family
