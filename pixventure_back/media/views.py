# media/views.py

import random
from django.db.models import Min, Max
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import MediaItem
from .serializers import MediaItemSerializer, UnpublishedMediaItemSerializer
from media.managers.media_item_creation_manager import MediaItemCreationManager
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
                status__in=[MediaItem.PENDING_MODERATION, MediaItem.APPROVED],
                post_links__isnull=True  # Only items that are not associated with any PostMedia
            )
            .prefetch_related("versions")
            .order_by("-created")
        )

class RandomMediaItemView(APIView):
    """
    API endpoint that returns a customizable number of random published MediaItem objects.

    - Limits the maximum number of items served to 30.
    - Uses repeated oversampling to efficiently retrieve random items from large datasets.
    - As a last-resort fallback, uses random ordering if repeated oversampling does not yield enough items.
    """
    serializer_class = MediaItemSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    
    def get(self, request, *args, **kwargs):
        # Parse and enforce the 'count' parameter; default is 10, maximum is 30.
        try:
            count = int(request.query_params.get('count', 10))
            if count <= 0:
                return Response(
                    {"detail": "Count must be a positive integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"detail": "Invalid count parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )
        required = min(count, 30)

        # Filter for published media items.
        qs = MediaItem.objects.filter(status=MediaItem.PUBLISHED)
        total = qs.count()
        if total == 0:
            return Response([], status=status.HTTP_200_OK)

        # Determine the min and max IDs in the queryset.
        min_id = qs.aggregate(Min('id'))['id__min']
        max_id = qs.aggregate(Max('id'))['id__max']

        # Use repeated oversampling to gather candidate items.
        candidate_dict = {}  # Mapping of id -> MediaItem
        attempts = 0
        max_attempts = 3  # Number of oversampling rounds before fallback

        while len(candidate_dict) < required and attempts < max_attempts:
            oversample_factor = 3
            num_to_sample = (required - len(candidate_dict)) * oversample_factor
            new_candidate_ids = {random.randint(min_id, max_id) for _ in range(num_to_sample)}
            # Exclude IDs already fetched
            new_candidate_ids = new_candidate_ids - set(candidate_dict.keys())
            new_items = qs.filter(id__in=new_candidate_ids)
            for item in new_items:
                candidate_dict[item.id] = item
            attempts += 1

        candidate_items = list(candidate_dict.values())

        # If still not enough, as a last resort, fetch additional items using random ordering.
        if len(candidate_items) < required:
            additional_needed = required - len(candidate_items)
            fallback_items = list(qs.order_by('?')[:additional_needed])
            candidate_items.extend(fallback_items)
        else:
            # Randomly select the required number from the candidate pool.
            candidate_items = random.sample(candidate_items, required)

        serializer = MediaItemSerializer(candidate_items, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
