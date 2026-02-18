from programs.models.residentials_models import ChildCaretakerAssignment, House
from rest_framework import serializers
from django.utils import timezone


class ChildCaretakerAssignmentWriteSerializer(serializers.ModelSerializer):
    caretaker_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = ChildCaretakerAssignment
        fields = [
            "id",
            "child",
            "caretaker_id",
            "assigned_date",
            "end_date",
            "is_active",
            "description",
        ]
        read_only_fields = ["id", "assigned_date"]

    def validate(self, attrs):
        caretaker_id = attrs.pop("caretaker_id")

        try:
            house = (
                House.objects
                .select_related("caretaker")
                .get(caretaker_id=caretaker_id)
            )
        except House.DoesNotExist:
            raise serializers.ValidationError(
                {"caretaker_id": "No house found for this caretaker."}
            )

        attrs["house"] = house
        child = attrs.get("child")

        if ChildCaretakerAssignment.objects.filter(
            child=child,
            house=house,
            is_active=True,
        ).exists():
            raise serializers.ValidationError(
                "This child already has an active assignment in this house."
            )

        return attrs

    def create(self, validated_data):
        validated_data["assigned_date"] = timezone.now().date()
        return super().create(validated_data)


class ChildCaretakerAssignmentReadSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.full_name", read_only=True)
    caretaker_name = serializers.CharField(
        source="house.caretaker.full_name",
        read_only=True
    )

    class Meta:
        model = ChildCaretakerAssignment
        fields = [
            "id",
            "child",
            "child_name",
            "caretaker_name",
            "assigned_date",
            "end_date",
            "is_active",
            "description",
        ]
