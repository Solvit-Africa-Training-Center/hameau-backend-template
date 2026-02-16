import logging
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from programs.models.ifashe_models import Sponsorship
from programs.serializers.ifashe_serializers import SponsorshipSerializer
from accounts.permissions import IsIfasheManager
from drf_spectacular.utils import extend_schema

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["IfasheTugufashe Program"],
)
class SponsorshipViewSet(viewsets.ModelViewSet):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    permission_classes = [IsIfasheManager]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "sponsorship_type"]
    search_fields = ["child__first_name", "child__last_name"]
    ordering_fields = ["start_date", "end_date", "created_on"]
    ordering = ["-created_on"]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            f"User {self.request.user} created a new sponsorship for child {instance.child} (ID: {instance.id})"
        )

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_status = old_instance.status
        instance = serializer.save()

        log_msg = f"User {self.request.user} updated sponsorship for child {instance.child} (ID: {instance.id})"
        if old_status != instance.status:
            log_msg += f" | Status changed from {old_status} to {instance.status}"

        logger.info(log_msg)

    def perform_destroy(self, instance):
        child_name = str(instance.child)
        s_id = instance.id
        instance.delete()
        logger.warning(
            f"User {self.request.user} deleted sponsorship for child {child_name} (ID: {s_id})"
        )

    @action(detail=False, methods=["get"])
    def sponsorship_stats(self, request):
        stats = {
            "active_sponsorships": self.queryset.filter(
                status=Sponsorship.ACTIVE
            ).count(),
            "total_sponsorships": self.queryset.count(),
            "by_type": self.queryset.values("sponsorship_type").annotate(
                count=Count("id")
            ),
            "by_status": self.queryset.values("status").annotate(count=Count("id")),
        }
        return Response(stats)
