from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from programs.models.ifashe_models import Sponsorship
from programs.serializers.ifashe_serializers import SponsorshipSerializer
from accounts.permissions import IsIfasheManager

class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'sponsorship_type']
    search_fields = ['child__first_name', 'child__last_name']
    ordering_fields = ['start_date', 'end_date', 'created_on']
    ordering = ['-created_on']

    @action(detail=False, methods=['get'])
    def sponsorship_stats(self, request):
        stats = {
            'active_sponsorships': self.queryset.filter(status=Sponsorship.ACTIVE).count(),
            'total_sponsorships': self.queryset.count(),
            'by_type': self.queryset.values('sponsorship_type').annotate(count=Count('id')),
            'by_status': self.queryset.values('status').annotate(count=Count('id'))
        }
        return Response(stats)
