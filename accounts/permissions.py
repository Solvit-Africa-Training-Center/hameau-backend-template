from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_superuser


class AdminBypassPermission(BasePermission):
    def is_system_admin(self, request):
        return request.user.is_authenticated and request.user.is_superuser

    def has_permission(self, request, view):
        if self.is_system_admin(request):
            return True
        return self.has_regular_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if self.is_system_admin(request):
            return True
        return self.has_regular_object_permission(request, view, obj)

    def has_regular_permission(self, request, view):
        return True

    def has_regular_object_permission(self, request, view, obj):
        return True


class HasRole(AdminBypassPermission):
    required_role = None

    def has_regular_permission(self, request, view):
        return (
            request.user.is_authenticated
            and self.required_role is not None
            and request.user.role == self.required_role
        )


class IsResidentialManager(HasRole):
    message = "Only the Residential Care program manager can perform this action."
    required_role = User.RESIDENTIAL_MANAGER


class IsInternshipManager(HasRole):
    message = (
        "Only the International Internship program manager can perform this action."
    )
    required_role = User.INTERNSHIP_MANAGER


class IsIfasheManager(HasRole):
    message = "Only the Ifashe Tugufashe program manager can perform this action."
    required_role = User.IFASHE_MANAGER


class IsOwner(AdminBypassPermission):
    message = "Only the owner can access this resource."

    def has_regular_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and hasattr(obj, "owner")
            and obj.owner == request.user
        )


class IsSystemAdmin(AdminBypassPermission):
    message = "Only system administrators can perform this action."

    def has_regular_permission(self, request, view):
        return False


class CanDestroyManager(AdminBypassPermission):
    def has_regular_object_permission(self, request, view, obj):
        if not (
            request.user.is_authenticated
            and hasattr(obj, "owner")
            and obj.owner == request.user
        ):
            return True
        return False
