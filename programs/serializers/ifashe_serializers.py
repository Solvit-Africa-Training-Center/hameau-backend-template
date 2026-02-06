<<<<<<< Updated upstream
=======
from django.utils import timezone
from rest_framework import serializers
from programs.models import (   Family, Parent, SponsoredChild, Sponsorship, SchoolSupport, SchoolPayment,
    DressingDistribution, ParentWorkContract, ParentAttendance, ParentPerformance
)
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


class SponsorshipSerializer(serializers.ModelSerializer):
    child_name = serializers.ReadOnlyField(source='child.full_name')

    class Meta:
        model = Sponsorship
        fields = [
            'id', 'child', 'child_name', 'sponsorship_type', 
            'start_date', 'end_date', 'status', 'pause_reason'
        ]
        
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError({
                "end_date": "End date must be after start date."
            })
            
        status = data.get('status')
        pause_reason = data.get('pause_reason')
        if status == Sponsorship.SUSPENDED and not pause_reason:
            raise serializers.ValidationError({
                "pause_reason": "Pause reason is required when status is Suspended."
            })
            
        return data


class SchoolPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolPayment
        fields = ['id', 'school_support', 'amount', 'date']

    def validate_amount(self, value):
        return validate_not_negative(value, "Payment amount")


class SchoolSupportSerializer(serializers.ModelSerializer):
    child_name = serializers.ReadOnlyField(source='child.full_name')
    school_name = serializers.ReadOnlyField(source='school.name')
    payments = SchoolPaymentSerializer(many=True, read_only=True)
    total_paid = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = SchoolSupport
        fields = [
            'id', 'child', 'child_name', 'school', 'school_name', 
            'academic_year', 'school_fees', 'materials_cost', 
            'total_cost', 'payment_status', 'notes', 
            'payments', 'total_paid', 'balance_due', 'is_overdue'
        ]
        
    def get_total_paid(self, obj):
        return sum(payment.amount for payment in obj.payments.all())
        
    def get_balance_due(self, obj):
        return obj.total_cost - self.get_total_paid(obj)
        
    def get_is_overdue(self, obj):
        return (
            obj.payment_status == SchoolSupport.PENDING or 
            obj.payment_status == SchoolSupport.OVERDUE
        ) and self.get_balance_due(obj) > 0


class IfasheChildSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    family_name = serializers.ReadOnlyField(source='family.family_name')
    family_id = serializers.PrimaryKeyRelatedField(
        source='family',
        queryset=Family.objects.all(),
        required=False
    )
    sponsorships = SponsorshipSerializer(many=True, read_only=True)
    school_support = SchoolSupportSerializer(many=True, read_only=True)

    class Meta:
        model = SponsoredChild
        fields = [
            'id', 'family_id', 'family_name', 'first_name', 'last_name', 
            'full_name', 'date_of_birth', 'gender', 'school_name', 
            'school_level', 'health_conditions', 'support_status', 
            'profile_image', 'birth_certificate', 'school_report',
            'sponsorships', 'school_support'
        ]
        extra_kwargs = {
            'gender': {'required': True},
            'school_name': {'required': True},
            'school_level': {'required': True},
        }

    def validate_date_of_birth(self, value):
        return validate_not_future_date(value, "Date of birth")


class IfasheFamilySerializer(serializers.ModelSerializer):
    parents = IfasheParentSerializer(many=True, required=False)
    children = IfasheChildSerializer(many=True, required=False)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = Family
        fields = [
            'id', 'family_name', 'address', 'province',
            'district', 'sector', 'cell', 'village',
            'vulnerability_level', 'housing_condition', 'family_members',
            'social_worker_assessment', 'proof_of_residence',
            'parents', 'children', 'children_count'
        ]
        # family_id removed from fields

    def validate_family_members(self, value):
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

class DressingDistributionSerializer(serializers.ModelSerializer):
    child_name = serializers.ReadOnlyField(source='child.full_name')

    class Meta:
        model = DressingDistribution
        fields = [
            'id', 'child', 'child_name', 'distribution_date', 
            'item_type', 'size', 'quantity', 'notes'
        ]

class ParentWorkContractSerializer(serializers.ModelSerializer):
    parent_name = serializers.ReadOnlyField(source='parent.full_name')
    supervisor_name = serializers.ReadOnlyField(source='supervisor.username')

    class Meta:
        model = ParentWorkContract
        fields = [
            'id', 'parent', 'parent_name', 'department', 
            'supervisor', 'supervisor_name',
            'contract_start_date', 'contract_end_date', 'status'
        ]

class ParentAttendanceSerializer(serializers.ModelSerializer):
    parent_name = serializers.ReadOnlyField(source='work_record.parent.full_name')
    department = serializers.ReadOnlyField(source='work_record.department')

    class Meta:
        model = ParentAttendance
        fields = [
            'id', 'work_record', 'parent_name', 'department',
            'attendance_date', 'status', 'notes'
        ]

class ParentPerformanceSerializer(serializers.ModelSerializer):
    parent_name = serializers.ReadOnlyField(source='work_record.parent.full_name')
    evaluator_name = serializers.ReadOnlyField(source='evaluated_by.username')

    class Meta:
        model = ParentPerformance
        fields = [
            'id', 'work_record', 'parent_name', 'evaluation_date', 
            'rating', 'comments', 'evaluated_by', 'evaluator_name'
        ]
    
>>>>>>> Stashed changes
