from rest_framework import serializers

from website_content.models import CompanyInfo, SocialMedia, WorkingDaysHours


class CompanyInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = [
            "id",
            "company_name",
            "company_description",
            "company_address",
            "company_phone",
            "company_email",
            "company_website",
            "company_logo",
            "created_at",
            "updated_at",
        ]


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ["id", "name", "url", "icon", "created_at", "updated_at"]


class WorkingDaysHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingDaysHours
        fields = ["id", "day", "start_hours", "end_hours", "close_days", "created_at", "updated_at"]
