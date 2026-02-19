from rest_framework import viewsets, mixins, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..models.content_models import PublicContent, TeamMember, ContactMessage
from ..serializers.content_serializers import PublicContentSerializer, TeamMemberSerializer, ContactMessageSerializer

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

class IsAdminUserOrReadOnly(AllowAny):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_staff

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        try:
            from utils.emails import send_contact_message_email
           
            send_contact_message_email(instance)
        except Exception as e:
           
            print(f"Failed to send email: {e}")

        headers = self.get_success_headers(serializer.data)
        return Response("Message submitted successfully", status=status.HTTP_201_CREATED, headers=headers)
