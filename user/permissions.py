from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from .satellite.models import Satellite
from .client.models import Client


class IsNotBlocked(permissions.BasePermission):
    """
    Custom permission to check if user is not blocked.
    Denies access to blocked users and effectively logs them out.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True  # Let other permissions handle unauthenticated users
        
        # Check if user is a Satellite
        if hasattr(request.user, 'satellite'):
            try:
                satellite = Satellite.objects.get(pk=request.user.pk)
                if satellite.blocked:
                    raise PermissionDenied("Your account has been blocked. Please contact support.")
                # Client doesn't have blocked field, so skip this check
            except Satellite.DoesNotExist:
                pass
        
        # Check if user is a Client - allow access to Client endpoints
        # Blocking is handled at the satellite level, not client level
        if hasattr(request.user, 'client'):
            # Client users should have access to Client endpoints
            # Individual satellite blocking is handled when accessing satellite-specific endpoints
            pass
        
        # For any User model that has blocked field
        if hasattr(request.user, 'blocked') and request.user.blocked:
            raise PermissionDenied("Your account has been blocked. Please contact support.")
        
        return True