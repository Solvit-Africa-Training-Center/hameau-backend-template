from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from public_modules.serializers.impact_serializers import ImpactStatsSerializer


class ImpactStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = ImpactStatsSerializer(instance={})
        return Response(serializer.data)
