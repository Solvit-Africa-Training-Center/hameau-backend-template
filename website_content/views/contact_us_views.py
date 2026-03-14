from rest_framework import viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema
from website_content.models import ContactMessage, ReplyToContactMessage
from website_content.serializers import ContactMessageSerializer,ReplyToContactMessageSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

@extend_schema(tags=["Contact Us"])
class ContactMessageCreateView(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def mark_as_read(self, request, *args, **kwargs):
        contact_message = self.get_object()
        contact_message.is_read = True
        contact_message.save()
        return Response({"message": "Contact message marked as read"})
    


@extend_schema(tags=["Contact Us"])
class ReplyToContactMessageCreateView(viewsets.ModelViewSet):
    queryset = ReplyToContactMessage.objects.all()
    serializer_class = ReplyToContactMessageSerializer
    permission_classes = [BasePermission]


    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    
