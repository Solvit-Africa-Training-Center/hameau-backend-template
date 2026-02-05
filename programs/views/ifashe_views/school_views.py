from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models

from programs.models.ifashe_models import SchoolSupport, SchoolPayment
from programs.serializers.ifashe_serializers import (
    SchoolSupportSerializer, SchoolPaymentSerializer
)
from accounts.permissions import IsIfasheManager

class SchoolSupportViewSet(viewsets.ModelViewSet):
    queryset = SchoolSupport.objects.all().prefetch_related('payments')
    serializer_class = SchoolSupportSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment_status', 'academic_year', 'school']
    search_fields = ['child__first_name', 'child__last_name', 'school__name']
    ordering_fields = ['created_on', 'academic_year']

    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        school_support = self.get_object()
        serializer = SchoolPaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(school_support=school_support)
            
            # Recalculate status
            total_paid = school_support.payments.aggregate(total=models.Sum('amount'))['total'] or 0
            if school_support.total_cost - total_paid <= 0:
                 school_support.payment_status = SchoolSupport.PAID
                 school_support.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
