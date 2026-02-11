from rest_framework import permissions

from history.middleware import get_current_user


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return str(get_current_user()) == "admin"
