from rest_framework import viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema

from website_content.serializers.team_models import TeamSerializer
from website_content.models.team_models import Team

@extend_schema(tags=["Teams"])
class TeamCreateView(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()