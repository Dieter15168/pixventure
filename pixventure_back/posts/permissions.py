# posts/permissions.py

from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Post

class IsPostOwnerOrAdminOrPublicRead(BasePermission):
    """
    Allows public read if the post is PUBLISHED.
    Otherwise, only the owner or a staff can perform any actions.
    """

    def has_object_permission(self, request, view, obj):
        # Public read if post is published
        if request.method in SAFE_METHODS and obj.status == Post.PUBLISHED:
            return True

        # Otherwise require post owner or staff
        return (obj.owner == request.user) or (request.user and request.user.is_staff)
