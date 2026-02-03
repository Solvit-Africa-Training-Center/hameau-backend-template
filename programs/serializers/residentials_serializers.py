import os
from rest_framework import serializers
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from django.db.models import Sum, Q, F
from ..models import (
    Child,
    ChildProgress,
    ProgressMedia,
    ChildEducation,
    EducationInstitution,
    EducationProgram,
    Caretaker,
    Caretaker,
    HealthRecord,
    ChildInsurance,
    ResidentialFinancialPlan,
)
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import ExtractMonth, ExtractYear


class ChildReadSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    end_date = serializers.DateField(read_only=True)

    class Meta:
        model = Child
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "gender",
            "date_of_birth",
            "age",
            "profile_image",
            "start_date",
            "end_date",
            "status",
            "special_needs",
            "vigilant_contact_name",
            "vigilant_contact_phone",
            "story",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


class ChildWriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Child
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "profile_image",
            "start_date",
            "special_needs",
            "vigilant_contact_name",
            "vigilant_contact_phone",
            "story",
        ]

    def validate_date_of_birth(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "Date of birth can not be in the future."
            )
        return value

    def validate_start_date(self, value):
        if value < timezone.now().date().replace(year=timezone.now().year - 10):
            raise serializers.ValidationError(
                "The date seems to be incorrect."
            )
        return value

    def validate(self, attrs):
        date_of_birth = attrs.get('date_of_birth')
        start_date = attrs.get('start_date')        
        if date_of_birth and start_date:
            if start_date < date_of_birth:
                raise serializers.ValidationError({
                    'start_date': "The starting date cannot be older that the date of birth"
                })        
        return attrs


class ProgressMediaWriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProgressMedia
        fields = [
            "progress_image",
            "progress_video",
        ]
    
    def validate_progress_video(self, video):
        allowed_extensions = [".mp4", ".mov", ".avi", ".mkv"]
        ext = os.path.splitext(video.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                "Not supported video format. Formats accepted : mp4, mov, avi, mkv."
            )
        return video

    def validate(self, attrs):
        if not attrs.get('progress_image') and not attrs.get('progress_video'):
            raise serializers.ValidationError(
                "Submit at least a video or an image"
            )
        return attrs


class ProgressMediaReadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProgressMedia
        fields = [
            "id",
            "progress_image",
            "progress_video",
            "created_on",
        ]
        read_only_fields = ["id", "created_on"]


class ChildProgressWriteSerializer(serializers.ModelSerializer):
    media = ProgressMediaWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = ChildProgress
        fields = [
            "notes",
            "media",
        ]

    def create(self, validated_data):
        media_data = validated_data.pop("media", [])
        
        child = self.context.get('child')
        if not child:
            raise serializers.ValidationError(
                "Child must be specified in context"
            )
        progress = ChildProgress.objects.create(child=child, **validated_data)
        for media in media_data:
            ProgressMedia.objects.create(progress=progress, **media)

        return progress


class ChildProgressReadSerializer(serializers.ModelSerializer):
    progress_media = ProgressMediaReadSerializer(many=True, read_only=True)

    class Meta:
        model = ChildProgress
        fields = [
            "id",
            "notes",
            "progress_media",
            "created_on",
        ]
        read_only_fields = ["id", "created_on"]


class EducationInstitutionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EducationInstitution
        fields = "__all__"
        read_only_fields = ["id", "created_on", "updated_on"]


class EducationProgramReadSerializer(serializers.ModelSerializer):
    institution = EducationInstitutionSerializer(read_only=True)

    class Meta:
        model = EducationProgram
        fields = "__all__"
        read_only_fields = ["id", "created_on", "updated_on"]


class EducationProgramWriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EducationProgram
        fields = [
            "institution",
            "program_name",
            "program_level",
            "cost",
        ]

    def validate_cost(self, value):
        if value is not None and value < Decimal('0'):
            raise serializers.ValidationError(
                "Cost must be positive."
            )
        return value


class ChildEducationWriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ChildEducation
        fields = [
            "child",
            "program",
            "start_date",
            "end_date",
            "status",
            "cost",
            "notes",
        ]

    def validate_cost(self, value):
        if value is not None and value < Decimal('0'):
            raise serializers.ValidationError(
                "Cost must be positive"
            )
        return value

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError({
                    'end_date': "End-date cannot come before start date"
                })
        
        return attrs


class ChildEducationReadSerializer(serializers.ModelSerializer):
    program = EducationProgramReadSerializer(read_only=True)
    child = ChildReadSerializer(read_only=True)

    class Meta:
        model = ChildEducation
        fields = [
            "id",
            "child",
            "program",
            "start_date",
            "end_date",
            "status",
            "cost",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


class CaretakerReadSerializer(serializers.ModelSerializer):
    """Serializer for reading caretaker data"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Caretaker
        fields = "__all__"
        read_only_fields = ('id', 'created_on', 'updated_on', 'deleted_on')


class CaretakerWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating caretaker data"""
    
    class Meta:
        model = Caretaker
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 
            'phone', 'email', 'address', 'role', 'hire_date', 'is_active'
        ]
        
    def validate_phone(self, value):
        """Validate phone number format"""
        if value and not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with country code (e.g., +250)")
        return value


class CaretakerListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Caretaker
        fields = [
            'id', 'full_name', 'first_name', 'last_name', 
            'phone', 'email', 'role', 'is_active', 'hire_date'
        ]

class HealthRecordReadSerializer(serializers.ModelSerializer):
    """Serializer for reading health records"""
    
    child_name = serializers.SerializerMethodField()
    child_details = ChildReadSerializer(source='child', read_only=True)
    cost_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthRecord
        fields = [
            'id', 'child', 'child_name', 'child_details', 'record_type',
            'visit_date', 'hospital_name', 'diagnosis', 'treatment',
            'description', 'cost', 'cost_formatted', 'created_on', 'updated_on'
        ]
        read_only_fields = ('id', 'created_on', 'updated_on')
    
    def get_child_name(self, obj):
        return f"{obj.child.first_name} {obj.child.last_name}"
    
    def get_cost_formatted(self, obj):
        """Format cost with currency"""
        return f"{obj.cost:,.2f} RWF"


class HealthRecordWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating health records"""
    
    class Meta:
        model = HealthRecord
        fields = [
            'child', 'record_type', 'visit_date', 'hospital_name',
            'diagnosis', 'treatment', 'description', 'cost'
        ]
    
    def validate_visit_date(self, value):
        """Ensure visit date is not in the future"""
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Visit date cannot be in the future")
        return value
    
    def validate_cost(self, value):
        """Ensure cost is not negative"""
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative")
        return value
    
    def validate(self, attrs):
        """Custom validation"""
        record_type = attrs.get('record_type')
        
        # Require diagnosis for illness records
        if record_type == 'Illness' and not attrs.get('diagnosis'):
            raise serializers.ValidationError({
                'diagnosis': 'Diagnosis is required for illness records'
            })
        
        # Require treatment for treatment records
        if record_type == 'Treatment' and not attrs.get('treatment'):
            raise serializers.ValidationError({
                'treatment': 'Treatment details are required for treatment records'
            })
        
        return attrs


class HealthRecordListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    
    child_name = serializers.SerializerMethodField()
    cost_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthRecord
        fields = [
            'id', 'child', 'child_name', 'record_type', 'visit_date',
            'hospital_name', 'diagnosis', 'cost', 'cost_formatted', 'created_on'
        ]
    
    def get_child_name(self, obj):
        return f"{obj.child.first_name} {obj.child.last_name}"
    
    
    def get_cost_formatted(self, obj):
        return f"{obj.cost:,.2f} RWF"


class SpendingReportSerializer(serializers.Serializer):
    """Serializer for residential spending report"""
    
    normal_spending = serializers.SerializerMethodField()
    special_diet_spending = serializers.SerializerMethodField()
    education_spending = serializers.SerializerMethodField()
    total_spending = serializers.SerializerMethodField()
    currency = serializers.CharField(default="RWF")
    
    def get_date_filters(self, date_field):
        request = self.context.get('request')
        filters = {}
        if request:
            start_date = request.query_params.get('start_date') or request.query_params.get('date_from')
            end_date = request.query_params.get('end_date') or request.query_params.get('date_to')
            
            if start_date:
                filters[f'{date_field}__gte'] = start_date
            if end_date:
                filters[f'{date_field}__lte'] = end_date
        return filters

    def _calculate_total_costs(self, children_queryset):

        health_filters = self.get_date_filters('visit_date')
        health_cost = HealthRecord.objects.filter(
            child__in=children_queryset, **health_filters
        ).aggregate(total=Sum('cost'))['total'] or Decimal('0.00')

        
        edu_filters = self.get_date_filters('start_date')
        edu_cost = ChildEducation.objects.filter(
            child__in=children_queryset, **edu_filters
        ).aggregate(total=Sum('cost'))['total'] or Decimal('0.00')

        
        ins_filters = self.get_date_filters('start_date')
        ins_cost = ChildInsurance.objects.filter(
            child__in=children_queryset, **ins_filters
        ).aggregate(total=Sum('cost'))['total'] or Decimal('0.00')
        
        
        plan_filters = self.get_date_filters('month')
        food_cost = ResidentialFinancialPlan.objects.filter(
            child__in=children_queryset, **plan_filters
        ).aggregate(total=Sum('food_cost'))['total'] or Decimal('0.00')

        return health_cost + edu_cost + ins_cost + food_cost

    def get_normal_spending(self, obj):
        # Children without special needs
        children = Child.objects.filter(
            Q(special_needs__isnull=True) | Q(special_needs__exact='')
        )
        return self._calculate_total_costs(children)

    def get_special_diet_spending(self, obj):
        # Children with special needs
        children = Child.objects.exclude(
            Q(special_needs__isnull=True) | Q(special_needs__exact='')
        )
        return self._calculate_total_costs(children)

    def get_education_spending(self, obj):
        # Total education spending for ALL children
        filters = self.get_date_filters('start_date')
        return ChildEducation.objects.filter(**filters).aggregate(total=Sum('cost'))['total'] or Decimal('0.00')


    def get_total_spending(self, obj):
        return self.get_normal_spending(obj) + self.get_special_diet_spending(obj)


class CostReportSerializer(serializers.Serializer):
    """Serializer for detailed cost report"""
    date_range = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    cost_by_type = serializers.SerializerMethodField()
    top_10_children_by_cost = serializers.SerializerMethodField()
    monthly_breakdown = serializers.SerializerMethodField()

    def _get_queryset(self):
        request = self.context.get('request')
        queryset = HealthRecord.objects.select_related('child')
        
        if request:
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            
            if date_from:
                queryset = queryset.filter(visit_date__gte=date_from)
            if date_to:
                queryset = queryset.filter(visit_date__lte=date_to)
        return queryset

    def get_date_range(self, obj):
        request = self.context.get('request')
        return {
            'from': request.query_params.get('date_from') if request else None,
            'to': request.query_params.get('date_to') if request else None
        }

    def get_total_cost(self, obj):
        queryset = self._get_queryset()
        return queryset.aggregate(total=Sum('cost'))['total'] or Decimal('0.00')

    def get_cost_by_type(self, obj):
        queryset = self._get_queryset()
        data = queryset.values('record_type').annotate(
            total_cost=Sum('cost'),
            count=Count('id'),
            average_cost=Avg('cost')
        ).order_by('-total_cost')
        
        return [
            {
                'record_type': item['record_type'],
                'total_cost': float(item['total_cost'] or 0),
                'count': item['count'],
                'average_cost': float(item['average_cost'] or 0),
            }
            for item in data
        ]

    def get_top_10_children_by_cost(self, obj):
        queryset = self._get_queryset()
        data = queryset.values(
            'child__id', 'child__first_name', 'child__last_name'
        ).annotate(
            total_cost=Sum('cost'),
            record_count=Count('id')
        ).order_by('-total_cost')[:10]
        
        return [
            {
                'child_id': str(item['child__id']),
                'child_name': f"{item['child__first_name']} {item['child__last_name']}",
                'total_cost': float(item['total_cost'] or 0),
                'record_count': item['record_count'],
            }
            for item in data
        ]

    def get_monthly_breakdown(self, obj):
        queryset = self._get_queryset()
        data = queryset.annotate(
            month=ExtractMonth('visit_date'),
            year=ExtractYear('visit_date')
        ).values('year', 'month').annotate(
            total_cost=Sum('cost'),
            count=Count('id')
        ).order_by('year', 'month')
        
        return [
            {
                'year': item['year'],
                'month': item['month'],
                'total_cost': float(item['total_cost'] or 0),
                'count': item['count'],
            }
            for item in data
        ]


class ChildProgressReportSerializer(serializers.Serializer):
    child = ChildReadSerializer(read_only=True)
    latest_progress = ChildProgressReadSerializer(read_only=True)
    previous_progress = ChildProgressReadSerializer(read_only=True)
    comparison_summary = serializers.SerializerMethodField()

    def get_comparison_summary(self, obj):
        latest = obj.get('latest_progress')
        previous = obj.get('previous_progress')
        
        if not latest:
            return "No progress records found."
        
        if not previous:
            return "Initial report. No previous records for comparison."
            
        return f"Comparison between {latest.created_on.date()} and {previous.created_on.date()}."


class FinancialReportDataSerializer(serializers.Serializer):
    report_type = serializers.CharField()
    title = serializers.CharField()
    data = serializers.ListField(child=serializers.DictField())
    date_range = serializers.DictField(required=False)

