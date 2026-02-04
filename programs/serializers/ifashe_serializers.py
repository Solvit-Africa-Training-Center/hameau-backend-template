from django.utils import timezone
from rest_framework import serializers
from programs.models import Family, Parent, SponsoredChild
import re


class IfasheParentSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    family_id = serializers.SlugRelatedField(
        source='family',
        slug_field='family_id',
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
        if value:
            if not value.isdigit() or len(value) != 16:
                raise serializers.ValidationError("National ID must be exactly 16 digits.")
        return value

    def validate_phone(self, value):
        if value:
            # Rwanda phone number regex: (07 | +2507 | 2507) followed by 8 digits
            pattern = r'^(07|\+2507|2507)[2389]\d{7}$'
            if not re.match(pattern, value):
                raise serializers.ValidationError("Invalid phone number format. Please use 07..., +2507..., or 2507...")
        return value

    def validate_date_of_birth(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_monthly_income(self, value):
        if value and value < 0:
            raise serializers.ValidationError("Monthly income cannot be negative.")
        return value

    def create(self, validated_data):
        return Parent.objects.create(**validated_data)


class IfasheChildSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    family_name = serializers.ReadOnlyField(source='family.family_name')
    family_id = serializers.SlugRelatedField(
        source='family',
        slug_field='family_id',
        queryset=Family.objects.all()
    )

    class Meta:
        model = SponsoredChild
        fields = [
            'id', 'family_id', 'family_name', 'first_name', 'last_name', 
            'full_name', 'date_of_birth', 'gender', 'school_name', 
            'school_level', 'health_conditions', 'support_status', 
            'profile_image', 'birth_certificate', 'school_report'
        ]

    def validate_date_of_birth(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def create(self, validated_data):
        return SponsoredChild.objects.create(**validated_data)


class IfasheFamilySerializer(serializers.ModelSerializer):
    parents = IfasheParentSerializer(many=True, required=False)
    children = IfasheChildSerializer(many=True, read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = [
            'id', 'family_name', 'family_id', 'address', 'province',
            'district', 'sector', 'cell', 'village',
            'vulnerability_level', 'housing_condition', 'family_members',
            'social_worker_assessment', 'proof_of_residence',
            'parents', 'children', 'children_count'
        ]
        extra_kwargs = {
            'family_id': {'read_only': True}
        }

    def validate_family_members(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError("Family members count must be at least 1.")
        return value

    def get_children_count(self, obj):
        return obj.children.count()

    def create(self, validated_data):
        parents_data = validated_data.pop('parents', [])
        family = Family.objects.create(**validated_data)
        for parent_data in parents_data:
            Parent.objects.create(family=family, **parent_data)
        return family
