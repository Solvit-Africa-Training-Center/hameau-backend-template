from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema

from public_modules.models import SuccessStory
from public_modules.serializers.story_serializers import SuccessStorySerializer
from utils.paginators import SmallResultsSetPagination


@extend_schema(tags=["Public Modules"])
class SuccessStoryViewSet(viewsets.ModelViewSet):
    queryset = SuccessStory.objects.all()
    serializer_class = SuccessStorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"] and not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True)
        return queryset
