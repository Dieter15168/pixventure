# media/views.py

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import MediaItem
from .serializers import MediaItemSerializer, UnpublishedMediaItemSerializer
from media.managers.media_item_creation_manager import MediaItemCreationManager
from rest_framework.exceptions import PermissionDenied
from .services.file_processor import process_uploaded_file

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
    Delegates creation logic to MediaItemCreationManager.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MediaItemSerializer

    def create(self, request, *args, **kwargs):
        upload_file = request.FILES.get("file")
        if not upload_file:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        result = MediaItemCreationManager.create_media_item(upload_file, request.user)
        if "error" in result:
            return Response({"detail": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "media_item_id": result["media_item_id"],
                "thumbnail_url": result.get("thumbnail_url"),
            },
            status=status.HTTP_201_CREATED
        )

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


class MediaItemAvailableForPostView(generics.ListAPIView):
    """
    Returns a list of media items for the authenticated user that
    are "Pending moderation", "Approved", or "Rejected" (i.e. available for new post usage)
    and that are not already used in any post.
    """
    serializer_class = UnpublishedMediaItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return (
            MediaItem.objects
            .filter(
                owner=self.request.user,
                status__in=[MediaItem.PENDING_MODERATION, MediaItem.APPROVED, MediaItem.REJECTED],
                post_links__isnull=True  # Only items that are not associated with any PostMedia
            )
            .prefetch_related("versions")
            .order_by("-created")
        )