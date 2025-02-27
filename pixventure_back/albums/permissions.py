# albums/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAlbumOwnerOrAdminOrPublicRead(BasePermission):
    """
    Allows public read if the album is PUBLIC.
    Otherwise, only the owner or a staff member can perform any actions.
    """

    def has_object_permission(self, request, view, obj):
        # If it's a safe method (GET, HEAD, OPTIONS) and the album is public, allow
        if request.method in SAFE_METHODS and obj.status == obj.PUBLIC:
            return True

        # Otherwise require album owner or staff
        return (obj.owner == request.user) or (request.user and request.user.is_staff)
