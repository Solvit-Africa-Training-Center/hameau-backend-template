from rest_framework import serializers


class ImpactStatsSerializer(serializers.Serializer):
    children_supported = serializers.IntegerField(read_only=True)
    years_of_service = serializers.IntegerField(read_only=True)
    families_empowered = serializers.IntegerField(read_only=True)
    youth_trained = serializers.IntegerField(read_only=True)
    school_enrollment = serializers.IntegerField(read_only=True)
