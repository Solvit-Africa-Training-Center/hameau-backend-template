# views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from programs.models import Caretaker
from programs.serializers import (
    CaretakerReadSerializer,
    CaretakerWriteSerializer,
    CaretakerListSerializer,
)
from utils.paginators import StandardResultsSetPagination
from accounts.permissions import IsResidentialManager


class CaretakerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing caretakers
    List, Create, Retrieve, Update, Delete operations for caretakers
    """
    queryset = Caretaker.objects.filter(deleted_on__isnull=True)
    permission_classes = [IsAuthenticated, IsResidentialManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["first_name", "last_name", "phone", "email", "role"]
    ordering_fields = [
        "first_name",
        "last_name",
        "hire_date",
        "created_on",
    ]
    ordering = ["-created_on"]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ["create", "update", "partial_update"]:
            return CaretakerWriteSerializer
        elif self.action == "list":
            return CaretakerListSerializer
        return CaretakerReadSerializer

    def get_queryset(self):
        """Filter queryset based on query params"""
        queryset = super().get_queryset()
        
        # Filter by active status
        if self.request.query_params.get("active_only") == "true":
            queryset = queryset.filter(is_active=True)
        
        # Filter by gender
        gender = self.request.query_params.get("gender")
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Filter by role
        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(role__icontains=role)
        
        return queryset

    def destroy(self, request, *args, **kwargs):
        """Soft delete caretaker"""
        instance = self.get_object()
        instance.delete()  # Soft delete
        return Response(
            {
                'success': True,
                'message': 'Caretaker deleted successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a caretaker"""
        caretaker = self.get_object()
        caretaker.is_active = True
        caretaker.save()
        
        serializer = self.get_serializer(caretaker)
        return Response(
            {
                'success': True,
                'message': 'Caretaker activated successfully',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a caretaker"""
        caretaker = self.get_object()
        caretaker.is_active = False
        caretaker.save()
        
        serializer = self.get_serializer(caretaker)
        return Response(
            {
                'success': True,
                'message': 'Caretaker deactivated successfully',
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get caretaker statistics"""
        queryset = self.get_queryset()
        
        total_caretakers = queryset.count()
        active_caretakers = queryset.filter(is_active=True).count()
        inactive_caretakers = queryset.filter(is_active=False).count()
        
        # Count by gender
        male_count = queryset.filter(gender=Caretaker.MALE).count()
        female_count = queryset.filter(gender=Caretaker.FEMALE).count()
        
        return Response(
            {
                'success': True,
                'data': {
                    'total_caretakers': total_caretakers,
                    'active_caretakers': active_caretakers,
                    'inactive_caretakers': inactive_caretakers,
                    'gender_breakdown': {
                        'male': male_count,
                        'female': female_count,
                    }
                }
            },
            status=status.HTTP_200_OK
        )