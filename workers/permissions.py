# workers/permissions.py
from rest_framework import permissions

class IsVerifiedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_profile_complete
        )