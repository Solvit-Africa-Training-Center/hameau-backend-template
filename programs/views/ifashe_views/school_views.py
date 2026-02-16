import logging
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models

from programs.models.ifashe_models import SchoolSupport
from programs.serializers.ifashe_serializers import (
    SchoolSupportSerializer, SchoolPaymentSerializer
)
from accounts.permissions import IsIfasheManager
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)

@extend_schema(
    tags=["IfasheTugufashe - Child School "],
)
class SchoolSupportViewSet(viewsets.ModelViewSet):
    queryset = SchoolSupport.objects.all().prefetch_related('payments')
    serializer_class = SchoolSupportSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment_status', 'academic_year', 'school']
    search_fields = ['child__first_name', 'child__last_name', 'school__name']
    ordering_fields = ['created_on', 'academic_year']

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} created school support for child {instance.child} (Year: {instance.academic_year})"
        )

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_status = old_instance.payment_status
        instance = serializer.save()
        
        log_msg = f"User {self.request.user} updated school support for child {instance.child} (Year: {instance.academic_year})"
        if old_status != instance.payment_status:
            log_msg += f" | Payment status changed from {old_status} to {instance.payment_status}"
        
        logger.info(log_msg)

    def perform_destroy(self, instance):
        child_name = str(instance.child)
        year = instance.academic_year
        instance.delete()
        logger.warning(
            f"User {self.request.user} deleted school support for child {child_name} (Year: {year})"
        )

    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        school_support = self.get_object()
        serializer = SchoolPaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            payment = serializer.save(school_support=school_support)
            
            logger.info(
                f"User {request.user} added payment of {payment.amount} for child {school_support.child} (ID: {school_support.id})"
            )
            
            total_paid = school_support.payments.aggregate(total=models.Sum('amount'))['total'] or 0
            if school_support.total_cost - total_paid <= 0:
                 school_support.payment_status = SchoolSupport.PAID
                 school_support.save()
                 logger.info(f"School support for child {school_support.child} is now fully PAID.")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
