from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from utils.permissions import IsAdminUserOrReadOnly

from public_modules.models.content_models import PublicContent, TeamMember, ContactMessage
from public_modules.serializers.content_serializers import PublicContentSerializer, TeamMemberSerializer, ContactMessageSerializer

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100

class BasePublicContentViewSet(viewsets.ReadOnlyModelViewSet):
   
    serializer_class = PublicContentSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return PublicContent.objects.filter(is_active=True).order_by('order', '-created_on')

class ImpactViewSet(BasePublicContentViewSet):
    pagination_class = None
    
    def get_queryset(self):
        return super().get_queryset().filter(category=PublicContent.CATEGORY_IMPACT)



class TeamViewSet(BasePublicContentViewSet):
    
    serializer_class = TeamMemberSerializer

    def get_queryset(self):
        return TeamMember.objects.filter(is_active=True).order_by('order', 'name')


class StoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUserOrReadOnly]
    serializer_class = PublicContentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return PublicContent.objects.filter(category=PublicContent.CATEGORY_SUCCESS_STORY).order_by('order', '-created_on')

class ContactMessageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
   
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination


