# views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from programs.models import HealthRecord
from programs.models import Child
from programs.serializers import (
    HealthRecordReadSerializer,
    HealthRecordWriteSerializer,
    HealthRecordListSerializer,
    SpendingReportSerializer,
)
from utils.filters.health_records_filters import HealthRecordFilter
from utils.paginators import StandardResultsSetPagination
from utils.search import CustomSearchFilter
from accounts.permissions import IsResidentialManager


class HealthRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing child health records
    
    Privacy: Only Residential Care Program Managers can access
    
    Features:
    - CRUD operations for health records
    - Cost tracking for health expenses
    - Filter by child, record type, date range, condition, cost
    - Search by diagnosis, treatment, hospital
    - Pagination
    """
    
    queryset = HealthRecord.objects.select_related('child')
    permission_classes = [IsAuthenticated, IsResidentialManager]
    filter_backends = [
        DjangoFilterBackend,
        CustomSearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = HealthRecordFilter
    search_fields = [
        'diagnosis', 'treatment', 'hospital_name', 
        'description', 'child__first_name', 'child__last_name'
    ]
    ordering_fields = [
        'visit_date', 'created_on', 'record_type', 'hospital_name', 'cost'
    ]
    ordering = ['-visit_date', '-created_on']
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ["create", "update", "partial_update"]:
            return HealthRecordWriteSerializer
        elif self.action == "list":
            return HealthRecordListSerializer
        return HealthRecordReadSerializer

    def get_queryset(self):
        """Filter queryset based on query params"""
        queryset = super().get_queryset()
        
        # Filter by specific child if provided
        child_id = self.request.query_params.get('child_id')
        if child_id:
            queryset = queryset.filter(child_id=child_id)
        
        # Filter by record type
        record_type = self.request.query_params.get('type')
        if record_type:
            queryset = queryset.filter(record_type=record_type)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(visit_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(visit_date__lte=date_to)
        
        return queryset

    def create(self, request, *args, **kwargs):
        """Create a new health record"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return detailed response
        read_serializer = HealthRecordReadSerializer(serializer.instance)
        return Response(
            {
                'success': True,
                'message': 'Health record created successfully',
                'data': read_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Update a health record"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        read_serializer = HealthRecordReadSerializer(serializer.instance)
        return Response(
            {
                'success': True,
                'message': 'Health record updated successfully',
                'data': read_serializer.data
            },
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a health record"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                'success': True,
                'message': 'Health record deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get health records statistics including cost analytics"""
        queryset = self.get_queryset()
        
        # Overall statistics
        total_records = queryset.count()
        
        # Cost statistics
        cost_stats = queryset.aggregate(
            total_cost=Sum('cost'),
            average_cost=Avg('cost'),
            max_cost=Max('cost'),
            min_cost=Min('cost')
        )
        
        # Count by record type with cost breakdown
        records_by_type = queryset.values('record_type').annotate(
            count=Count('id'),
            total_cost=Sum('cost'),
            average_cost=Avg('cost')
        ).order_by('-total_cost')
        
        # Recent records (last 30 days)
        from datetime import timedelta
        from django.utils import timezone
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_records = queryset.filter(visit_date__gte=thirty_days_ago)
        recent_cost = recent_records.aggregate(total=Sum('cost'))['total'] or Decimal('0.00')
        
        # Children with health records
        children_with_records = queryset.values('child').distinct().count()
        
        return Response(
            {
                'success': True,
                'data': {
                    'total_records': total_records,
                    'recent_records_30_days': recent_records.count(),
                    'recent_cost_30_days': float(recent_cost),
                    'children_with_records': children_with_records,
                    'cost_statistics': {
                        'total_cost': float(cost_stats['total_cost'] or 0),
                        'average_cost': float(cost_stats['average_cost'] or 0),
                        'max_cost': float(cost_stats['max_cost'] or 0),
                        'min_cost': float(cost_stats['min_cost'] or 0),
                    },
                    'records_by_type': [
                        {
                            'record_type': item['record_type'],
                            'count': item['count'],
                            'total_cost': float(item['total_cost'] or 0),
                            'average_cost': float(item['average_cost'] or 0),
                        }
                        for item in records_by_type
                    ],
                }
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='child/(?P<child_id>[^/.]+)')
    def child_records(self, request, child_id=None):
        """Get all health records for a specific child with cost summary"""
        child = get_object_or_404(Child, pk=child_id)
        records = self.get_queryset().filter(child=child)
        
        # Calculate total cost for this child
        total_cost = records.aggregate(total=Sum('cost'))['total'] or Decimal('0.00')
        average_cost = records.aggregate(avg=Avg('cost'))['avg'] or Decimal('0.00')
        
        # Paginate results
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = HealthRecordReadSerializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data['child_name'] = f"{child.first_name} {child.last_name}"
            response_data['cost_summary'] = {
                'total_cost': float(total_cost),
                'average_cost': float(average_cost),
                'record_count': records.count()
            }
            return Response(response_data)
        
        serializer = HealthRecordReadSerializer(records, many=True)
        return Response(
            {
                'success': True,
                'child_name': f"{child.first_name} {child.last_name}",
                'count': records.count(),
                'cost_summary': {
                    'total_cost': float(total_cost),
                    'average_cost': float(average_cost),
                },
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def by_condition(self, request):
        """Filter records by medical condition/diagnosis"""
        condition = request.query_params.get('condition')
        
        if not condition:
            return Response(
                {
                    'success': False,
                    'message': 'Condition parameter is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        records = self.get_queryset().filter(
            Q(diagnosis__icontains=condition) | 
            Q(treatment__icontains=condition) |
            Q(description__icontains=condition)
        )
        
        # Calculate cost for this condition
        total_cost = records.aggregate(total=Sum('cost'))['total'] or Decimal('0.00')
        
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = HealthRecordListSerializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data['condition'] = condition
            response_data['total_cost'] = float(total_cost)
            return Response(response_data)
        
        serializer = HealthRecordListSerializer(records, many=True)
        return Response(
            {
                'success': True,
                'condition': condition,
                'count': records.count(),
                'total_cost': float(total_cost),
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def cost_report(self, request):
        """Generate a detailed cost report"""
        queryset = self.get_queryset()
        
        # Get date range from query params
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(visit_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(visit_date__lte=date_to)
        
        # Overall cost statistics
        total_cost = queryset.aggregate(total=Sum('cost'))['total'] or Decimal('0.00')
        
        # Cost by record type
        cost_by_type = queryset.values('record_type').annotate(
            total_cost=Sum('cost'),
            count=Count('id'),
            average_cost=Avg('cost')
        ).order_by('-total_cost')
        
        # Cost by child (top 10 most expensive)
        cost_by_child = queryset.values(
            'child__id', 'child__first_name', 'child__last_name'
        ).annotate(
            total_cost=Sum('cost'),
            record_count=Count('id')
        ).order_by('-total_cost')[:10]
        
        # Monthly breakdown (if date range spans multiple months)
        monthly_costs = queryset.extra(
            select={'month': 'EXTRACT(month FROM visit_date)', 'year': 'EXTRACT(year FROM visit_date)'}
        ).values('year', 'month').annotate(
            total_cost=Sum('cost'),
            count=Count('id')
        ).order_by('year', 'month')
        
        return Response(
            {
                'success': True,
                'date_range': {
                    'from': date_from,
                    'to': date_to
                },
                'total_cost': float(total_cost),
                'cost_by_type': [
                    {
                        'record_type': item['record_type'],
                        'total_cost': float(item['total_cost'] or 0),
                        'count': item['count'],
                        'average_cost': float(item['average_cost'] or 0),
                    }
                    for item in cost_by_type
                ],
                'top_10_children_by_cost': [
                    {
                        'child_id': str(item['child__id']),
                        'child_name': f"{item['child__first_name']} {item['child__last_name']}",
                        'total_cost': float(item['total_cost'] or 0),
                        'record_count': item['record_count'],
                    }
                    for item in cost_by_child
                ],
                'monthly_breakdown': [
                    {
                        'year': int(item['year']),
                        'month': int(item['month']),
                        'total_cost': float(item['total_cost'] or 0),
                        'count': item['count'],
                    }
                    for item in monthly_costs
                ]
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def spending_summary(self, request):
        """
        Get spending summary for:
        - Normal health spending (kids without special diets)
        - Special diet spending (kids with special diets)
        - Education spending
        """
        return Response(
            {
                'success': True,
                'data': SpendingReportSerializer({}, context={'request': request}).data
            },
            status=status.HTTP_200_OK
        )