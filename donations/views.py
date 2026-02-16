from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Donor, Donation, SponsorEmailLog
from .serializers import DonorSerializer, DonationSerializer, SponsorEmailLogSerializer

class DonorViewSet(viewsets.ModelViewSet):
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["donor_type"]
    search_fields = ["fullname", "email", "phone"]
    ordering_fields = ["fullname", "created_on"]

    @action(detail=True, methods=["get"])
    def donations(self, request, pk=None):
        donor = self.get_object()
        donations = donor.donations.all()
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data)


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["donor", "child", "payment_method", "currency"]
    search_fields = ["donation_purpose", "notes"]
    ordering_fields = ["donation_date", "amount"]


class SponsorEmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SponsorEmailLog.objects.all()
    serializer_class = SponsorEmailLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["donor", "child", "status", "month", "year"]
    ordering_fields = ["sent_at"]
