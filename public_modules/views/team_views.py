from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema

from public_modules.models import TeamMember
from public_modules.serializers.team_serializers import TeamMemberSerializer
from utils.paginators import SmallResultsSetPagination


@extend_schema(tags=["Public Modules"])
class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"] and not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        return queryset
