from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import Parent, ParentWorkContract, ParentAttendance, ParentPerformance
from programs.serializers.ifashe_serializers import (
    IfasheParentSerializer, 
    ParentWorkContractSerializer, 
    ParentAttendanceSerializer, 
    ParentPerformanceSerializer
)
from accounts.permissions import IsIfasheManager


class IfasheParentViewSet(viewsets.ModelViewSet):
    queryset = Parent.objects.all().select_related('family')
    serializer_class = IfasheParentSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'relationship', 'marital_status']
    search_fields = ['first_name', 'last_name', 'national_id', 'phone']
    ordering_fields = ['created_on', 'first_name', 'last_name']
    ordering = ['-created_on']

class ParentWorkContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Parent Work Contracts (Assignments).
    """
    queryset = ParentWorkContract.objects.all().select_related('parent', 'supervisor')
    serializer_class = ParentWorkContractSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'department', 'parent']
    search_fields = ['parent__first_name', 'parent__last_name', 'department', 'job_role'] # job_role backup
    ordering_fields = ['contract_start_date', 'status']
    ordering = ['-contract_start_date']

class ParentAttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Parent Attendance.
    """
    queryset = ParentAttendance.objects.all().select_related('work_record__parent')
    serializer_class = ParentAttendanceSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'attendance_date', 'work_record__department']
    search_fields = ['work_record__parent__first_name', 'work_record__parent__last_name', 'notes']
    ordering_fields = ['attendance_date']
    ordering = ['-attendance_date']

class ParentPerformanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Parent Performance (Evaluations).
    """
    queryset = ParentPerformance.objects.all().select_related('work_record__parent', 'evaluated_by')
    serializer_class = ParentPerformanceSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating', 'evaluation_date']
    search_fields = ['work_record__parent__first_name', 'work_record__parent__last_name', 'comments']
    ordering_fields = ['evaluation_date', 'rating']
    ordering = ['-evaluation_date']
