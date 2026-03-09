from rest_framework import serializers

from website_content.models import CompanyImpact


class CompanyImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyImpact
        fields = [
            "id",
            "children_supported",
            "years_of_service",
            "families_strengthened",
            "communities_impacted",
            "schools_supported",
            "youth_trained",
            "success_rate",
            "created_at",
            "updated_at",
        ]
