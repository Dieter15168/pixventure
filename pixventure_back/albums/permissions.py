# albums/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAlbumOwnerOrAdminOrPublicRead(BasePermission):
    """
    Allows public read if the album is PUBLIC.
    Otherwise, only the owner or a staff member can perform any actions.
    Works with both Album and AlbumElement objects.
    """
    def has_object_permission(self, request, view, obj):
        # If obj is an AlbumElement, use its parent album for permission checks.
        album = getattr(obj, 'album', obj)

        if request.method in SAFE_METHODS and album.status == album.PUBLIC:
            return True

        return (album.owner == request.user) or (request.user and request.user.is_staff)
