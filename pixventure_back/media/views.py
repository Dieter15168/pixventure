# media/views.py

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import MediaItem
from .serializers import MediaItemSerializer
from rest_framework.exceptions import PermissionDenied

class MediaItemListView(generics.ListAPIView):
    """
    GET /api/media/
    Returns a paginated list of media items for the authenticated user.
    """
    serializer_class = MediaItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MediaItem.objects.filter(owner=self.request.user).order_by('-created')

class MediaItemCreateView(generics.CreateAPIView):
    """
    POST /api/media/new/
    Creates a new media item from a file uploaded by the user.
    """
    serializer_class = MediaItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MediaItemDetailView(generics.RetrieveAPIView):
    """
    GET /api/media/<pk>/
    Returns the details of a media item (like ID, type, thumbnail, etc.)
    """
    queryset = MediaItem.objects.all()
    serializer_class = MediaItemSerializer
    permission_classes = [IsAuthenticated]

class MediaItemDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/media/<pk>/delete/
    Deletes a media item. Only the owner or admin can delete the media item.
    """
    queryset = MediaItem.objects.all()
    serializer_class = MediaItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        # Ensure the user is either the owner or an admin
        if instance.owner != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("You do not have permission to delete this media item.")
        instance.delete()
