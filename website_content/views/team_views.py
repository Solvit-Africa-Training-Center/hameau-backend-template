from rest_framework import serializers, viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema

from website_content.serializers.team_serializers import TeamSerializer
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

    def list(self, request, *args, **kwargs):
        serializers=TeamSerializer(self.get_queryset(), many=True)
        return Response(serializers.data)