# media/views.py

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MediaItem
from .serializers import MediaItemSerializer
from rest_framework.exceptions import PermissionDenied
from .services.item_management import process_uploaded_file

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
    Creates a new media item from a single file uploaded by the user.
    We move complexity to an external service function: `process_uploaded_file`.
    """
    serializer_class = MediaItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Expecting 'file' in request.FILES
        upload_file = request.FILES.get('file')
        if not upload_file:
            return Response({"detail": "No file found. Please attach a file under 'file'."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # We'll handle validations, hashing, dedup, etc. in a separate service function:
        result = process_uploaded_file(upload_file, request.user)
        if result.get("error"):
            return Response({"detail": result["error"]}, status=status.HTTP_400_BAD_REQUEST)
        
        # If success, 'result' includes the created MediaItem object
        media_item = result["media_item"]
        
        # Return the standard serializer output
        serializer = self.get_serializer(media_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
