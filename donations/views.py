from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Donor, Donation, SponsorEmailLog
from .serializers import DonorSerializer, DonationSerializer, SponsorEmailLogSerializer
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Donations"],
)
class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["donor_type"]
    search_fields = ["fullname", "email", "phone"]
    ordering_fields = ["fullname", "created_on"]


@extend_schema(
    tags=["Donations"],
)
class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "donation_type",
        "donor",
        "child",
        "family",
        "currency",
        "payment_method",
    ]
    search_fields = ["donation_purpose", "notes", "donor__fullname"]
    ordering_fields = ["donation_date", "amount", "created_on"]

    def perform_create(self, serializer):
        serializer.save()


@extend_schema(
    tags=["Donations"],
)
class SponsorEmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SponsorEmailLog.objects.all()
    serializer_class = SponsorEmailLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["donor", "child", "month", "year", "status"]
    ordering_fields = ["sent_at"]
