from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from ..models.team_models import TeamMember
from ..serializers.team_serializers import TeamMemberSerializer


class TeamMemberListView(APIView):
 
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Team"],
        summary="Get team members",
        description="Retrieve all active team members displayed on the Meet Our Team page.",
        responses={200: TeamMemberSerializer(many=True)},
    )
    def get(self, request):
        members = TeamMember.objects.filter(is_active=True)
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)


class TeamMemberViewSet(viewsets.ModelViewSet):
   
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    
