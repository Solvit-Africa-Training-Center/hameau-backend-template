import django_filters
from django.db.models import Q
from programs.models import HealthRecord


class HealthRecordFilter(django_filters.FilterSet):
    """Filter for health records"""
    
    child = django_filters.UUIDFilter(field_name='child__id')
    record_type = django_filters.ChoiceFilter(choices=HealthRecord.RECORD_TYPE_CHOICES)
    visit_date_from = django_filters.DateFilter(field_name='visit_date', lookup_expr='gte')
    visit_date_to = django_filters.DateFilter(field_name='visit_date', lookup_expr='lte')
    hospital = django_filters.CharFilter(field_name='hospital_name', lookup_expr='icontains')
    diagnosis = django_filters.CharFilter(field_name='diagnosis', lookup_expr='icontains')
    treatment = django_filters.CharFilter(field_name='treatment', lookup_expr='icontains')

    # Cost filters
    cost_min = django_filters.NumberFilter(field_name='cost', lookup_expr='gte')
    cost_max = django_filters.NumberFilter(field_name='cost', lookup_expr='lte')
    cost_exact = django_filters.NumberFilter(field_name='cost', lookup_expr='exact')
    
    # Date range shortcuts
    year = django_filters.NumberFilter(field_name='visit_date', lookup_expr='year')
    month = django_filters.NumberFilter(field_name='visit_date', lookup_expr='month')
    
    class Meta:
        model = HealthRecord
        fields = ['child', 'record_type', 'hospital']