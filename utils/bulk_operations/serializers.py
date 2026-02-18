from rest_framework import serializers


class BulkActionSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)
    payload = serializers.DictField(required=False)

    def validate_ids(self, value):
        model = self.context.get("model")
        max_size = self.context.get("max_bulk_size")

        if not model:
            raise serializers.ValidationError(
                "Model must be provided in serializer context."
            )

        if max_size and len(value) > max_size:
            raise serializers.ValidationError(
                f"Bulk operation limited to {max_size} items. You sent {len(value)}."
            )

        existing_ids = set(
            model.objects.filter(pk__in=value).values_list("pk", flat=True)
        )

        missing_ids = set(value) - existing_ids

        if missing_ids:
            raise serializers.ValidationError(
                f"Some IDs do not exist: {list(missing_ids)}"
            )

        return value
