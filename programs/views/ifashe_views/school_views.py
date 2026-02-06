from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from programs.models.ifashe_models import SchoolPayment, SchoolSupport
from programs.serializers.ifashe_serializers import SchoolPaymentSerializer

class SchoolPaymentViewSet(viewsets.ModelViewSet):
    queryset = SchoolPayment.objects.all()
    serializer_class = SchoolPaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['school_support', 'status', 'payment_date']
    search_fields = ['receipt_number', 'notes']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']

    def perform_create(self, serializer):
        payment = serializer.save()
        # Update SchoolSupport payment status logic could go here
        # Example: check total paid vs fees and update status
        self._update_school_support_status(payment.school_support)

    def perform_update(self, serializer):
        payment = serializer.save()
        self._update_school_support_status(payment.school_support)

    def _update_school_support_status(self, school_support):
        # Allow manual override, but if status is pending, maybe auto-update?
        # Keeping it simple for restoration: just recalculate if needed.
        # For now, just save to trigger any signals if they exist.
        school_support.save()
