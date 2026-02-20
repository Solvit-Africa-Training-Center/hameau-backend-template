from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from accounts.permissions import IsAdminOrReadOnly
from ..models.content_models import PublicContent, ContactMessage, TeamMember, SuccessStory
from .content_serializers import (
    PublicContentSerializer,
    ContactMessageSerializer,
    TeamMemberSerializer,
    SuccessStorySerializer
)
from ..pagination import PublicModulePagination

class PublicContentViewSet(viewsets.ModelViewSet):
    queryset = PublicContent.objects.all()
    serializer_class = PublicContentSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PublicModulePagination

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    pagination_class = PublicModulePagination

class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PublicModulePagination

class SuccessStoryViewSet(viewsets.ModelViewSet):
    queryset = SuccessStory.objects.all()
    serializer_class = SuccessStorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PublicModulePagination
