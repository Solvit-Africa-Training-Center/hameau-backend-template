import logging
from accounts.models import ActivityLog

def record_activity(request, action, user=None, resource=None, resource_id=None, details=None):
    """
    Utility function to record system activities.

    :param request: The HTTP request object (used to get IP address)
    :param action: A string describing the action (e.g., 'LOGIN', 'CREATE_CHILD')
    :param user: The user performing the action (optional, derived from request if not provided)
    :param resource: The name of the resource being acted upon (e.g., 'Child')
    :param resource_id: The ID of the resource (optional)
    :param details: A dictionary containing additional information (optional)
    """
    logger = logging.getLogger(__name__)
    ip_address = None

    if request:
        if user is None and hasattr(request, "user") and request.user.is_authenticated:
            user = request.user

        # Get IP Address
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0]
        else:
            ip_address = request.META.get("REMOTE_ADDR")

    try:
        ActivityLog.objects.create(
            user=user,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )
    except Exception as e:
        logger.error(f"Failed to record activity: {str(e)}")
