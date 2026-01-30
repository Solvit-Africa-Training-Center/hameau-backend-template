from rest_framework.permissions import BasePermission
# from django.contrib.auth.models import AnonymousUser
from .models import User


class IsSystemAdmin(BasePermission):
    message = "Only system administrators can perfom this action"    

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )


class HasRole(BasePermission):    
    required_role = None

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and self.required_role is not None
            and request.user.role == self.required_role
        )


class IsResidentialManager(HasRole):
    message = "Only the Residential Care program can perform this"
    required_role = User.RESIDENTIAL_MANAGER


class IsInternshipManager(HasRole):
    message = "Only the manager of International Internship program can perform this"
    required_role = User.INTERNSHIP_MANAGER


class IsIfasheManager(HasRole):
    message = "Only the manager of Ifashe Tugufashe program can perform this"
    required_role = User.IFASHE_MANAGER


class IsOwner(BasePermission):    
    message = "Only the owner can access this resource"

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and hasattr(obj, "owner")
            and obj.owner == request.user
        )

class CanDestroyManager(BasePermission):   

    def has_object_permission(self, request, view, obj):
        if not (request.user.is_authenticated and hasattr(obj, "owner")  and obj.owner == request.user) :
            return True
        return False
            