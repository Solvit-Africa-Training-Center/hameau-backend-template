from rest_framework import permissions

class IsInternshipManager(permissions.BasePermission):
    """
    Allows access only to users with the INTERNSHIP_MANAGER role.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role == "INTERNSHIPS_MANAGER" or request.user.is_staff or request.user.role == "SYSTEM_ADMIN"
