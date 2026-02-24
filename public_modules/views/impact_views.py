from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from public_modules.serializers.impact_serializers import ImpactStatsSerializer

@extend_schema(tags=["Public Modules"])
class ImpactStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = ImpactStatsSerializer(instance={})
        return Response(serializer.data)
