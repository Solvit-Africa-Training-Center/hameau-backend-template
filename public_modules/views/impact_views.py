from django.db.models import Min, Q
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from programs.models import (
    Child,
    ChildEducation,
    Family,
    InternshipApplication,
    SchoolSupport,
    SponsoredChild,
    Sponsorship,
)
from public_modules.serializers.impact_serializers import ImpactStatsSerializer


def _has_field(model, field_name: str) -> bool:
    return any(field.name == field_name for field in model._meta.fields)


class ImpactStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        children_supported = SponsoredChild.objects.values(
            "first_name",
            "last_name",
            "date_of_birth",
        ).union(
            Child.objects.values(
                "first_name",
                "last_name",
                "date_of_birth",
            )
        ).count()

        ifashe_start = Sponsorship.objects.aggregate(start=Min("start_date"))["start"]
        residential_start = Child.objects.aggregate(start=Min("start_date"))["start"]
        start_dates = [date for date in [ifashe_start, residential_start] if date]
        earliest_start = min(start_dates) if start_dates else None

        years_of_service = 0
        if earliest_start:
            today = timezone.now().date()
            years_of_service = today.year - earliest_start.year - (
                (today.month, today.day) < (earliest_start.month, earliest_start.day)
            )

        families_empowered = Family.objects.count()
        youth_trained = InternshipApplication.objects.filter(
            status=InternshipApplication.APPROVED
        ).count()

        school_support_active_or_paid = Q(payment_status=SchoolSupport.PAID)
        if _has_field(SchoolSupport, "is_active"):
            school_support_active_or_paid |= Q(is_active=True)
        else:
            school_support_active_or_paid |= Q(child__support_status=SponsoredChild.ACTIVE)

        child_education_active = Q(status=ChildEducation.ACTIVE)
        if _has_field(ChildEducation, "is_active"):
            child_education_active |= Q(is_active=True)
        else:
            child_education_active |= Q(child__status=Child.ACTIVE)

        school_enrollment = SchoolSupport.objects.filter(
            school_support_active_or_paid
        ).count() + ChildEducation.objects.filter(child_education_active).count()

        serializer = ImpactStatsSerializer(
            data={
                "children_supported": children_supported,
                "years_of_service": years_of_service,
                "families_empowered": families_empowered,
                "youth_trained": youth_trained,
                "school_enrollment": school_enrollment,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
