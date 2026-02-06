from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from programs.models import ParentWorkContract, ParentAttendance, ParentPerformance
from programs.serializers.ifashe_serializers import (
    ParentWorkContractSerializer, 
    ParentAttendanceSerializer, 
    ParentPerformanceSerializer
)
from accounts.permissions import IsIfasheManager

class ParentWorkContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Parent Work Contracts.
    """
    queryset = ParentWorkContract.objects.all().select_related('parent')
    serializer_class = ParentWorkContractSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'parent']
    search_fields = ['parent__first_name', 'parent__last_name', 'job_role']
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
    filterset_fields = ['status', 'attendance_date']
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
