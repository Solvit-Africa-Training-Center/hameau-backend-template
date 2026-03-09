from rest_framework import viewsets
from rest_framework.permissions import BasePermission,AllowAny
from drf_spectacular.utils import extend_schema

from website_content.serializers.testimonial_serializers import TestimonialSerializer
from website_content.models.testimonial_models import Testimonial

@extend_schema(tags=["Testimonials"])
class TestimonialCreateView(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [BasePermission]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return super().get_permissions()