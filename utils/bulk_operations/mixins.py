from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from .serializers import BulkActionSerializer


class BulkActionMixin:
    bulk_serializer_class = BulkActionSerializer
    bulk_atomic = True
    bulk_max_size = 100
    bulk_async_threshold = 50

    def get_bulk_serializer(self, *args, **kwargs):
        kwargs.setdefault("context", {})
        kwargs["context"]["model"] = self.get_queryset().model
        kwargs["context"]["max_bulk_size"] = self.bulk_max_size
        return self.bulk_serializer_class(*args, **kwargs)

    def perform_bulk_action(
        self,
        request,
        action_type="delete",
        custom_handler=None,
        async_task=None,
        success_status=status.HTTP_200_OK,
        extra_filters=None,
    ):
        serializer = self.get_bulk_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data["ids"]
        payload = serializer.validated_data.get("payload", {})

        queryset = self.get_queryset().filter(pk__in=ids)

        if extra_filters:
            queryset = queryset.filter(**extra_filters)

        if (
            async_task
            and action_type in ["delete", "update"]
            and len(ids) >= self.bulk_async_threshold
        ):
            async_task.delay(
                ids=[str(i) for i in ids],
                payload=payload,
                action_type=action_type,
                model_label=self.get_queryset().model._meta.label,
            )

            return Response(
                {
                    "message": "Bulk operation scheduled asynchronously.",
                    "action": action_type,
                    "count": len(ids),
                    "async": True,
                },
                status=status.HTTP_202_ACCEPTED,
            )

        try:
            if self.bulk_atomic:
                context_manager = transaction.atomic()
            else:
                context_manager = transaction.atomic()

            with context_manager:
                if action_type == "delete":
                    count = queryset.count()
                    queryset.delete()

                    result = {
                        "message": f"{count} objects deleted successfully.",
                        "action": "delete",
                        "count": count,
                        "async": False,
                    }

                elif action_type == "update":
                    if not payload:
                        return Response(
                            {"detail": "Payload is required for update."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    count = queryset.update(**payload)

                    result = {
                        "message": f"{count} objects updated successfully.",
                        "action": "update",
                        "count": count,
                        "updated_fields": list(payload.keys()),
                        "async": False,
                    }

                elif action_type == "custom":
                    if not custom_handler:
                        raise ValueError("Custom handler must be provided.")

                    result = custom_handler(queryset, payload)
                    result.setdefault("async", False)

                else:
                    return Response(
                        {"detail": "Invalid bulk action type."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Exception as e:
            return Response(
                {
                    "message": "Bulk operation failed.",
                    "error": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(result, status=success_status)
