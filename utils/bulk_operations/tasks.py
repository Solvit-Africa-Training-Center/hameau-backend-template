from celery import shared_task
from django.apps import apps
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def generic_bulk_task(self, ids, payload, action_type, model_label):
    try:
        model = apps.get_model(model_label)
        if not model:
            raise LookupError(f"Model {model_label} not found.")
    except LookupError as e:
        logger.error(str(e))
        raise

    queryset = model.objects.filter(pk__in=ids)

    result = {
        "model": model_label,
        "action": action_type,
        "requested_count": len(ids),
        "affected_count": 0,
        "async": True,
    }

    try:
        with transaction.atomic():
            if action_type == "delete":
                count = queryset.count()
                queryset.delete()
                result["affected_count"] = count

            elif action_type == "update":
                if not payload:
                    raise ValueError("Payload is required for update.")

                count = queryset.update(**payload)
                result["affected_count"] = count
                result["updated_fields"] = list(payload.keys())

            else:
                raise ValueError(f"Unsupported async action: {action_type}")

    except Exception as e:
        logger.exception("Bulk async operation failed.")
        raise e

    logger.info(
        f"Bulk async completed | Model={model_label} | "
        f"Action={action_type} | Affected={result['affected_count']}"
    )

    return result
