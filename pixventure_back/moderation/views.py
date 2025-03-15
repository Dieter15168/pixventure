# moderation/views.py

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from posts.models import Post
from media.models import MediaItem
from .serializers import PostModerationSerializer, ModerationActionCreateSerializer
from media.serializers import UnpublishedMediaItemSerializer

class ModerationDashboardView(generics.ListAPIView):
    """
    Returns posts and orphan media items pending moderation.
    Access is allowed only for admin users.
    """
    permission_classes = [IsAdminUser]  # Replace with custom admin check if needed
    pagination_class = None

    def list(self, request, *args, **kwargs):
        # Get posts pending moderation that are not yet approved or published.
        posts_qs = Post.objects.filter(
            status=Post.PENDING_MODERATION
        ).prefetch_related("post_media_links__media_item").order_by("-created")

        # Get media items pending moderation that are not associated with any post.
        orphan_media_qs = MediaItem.objects.filter(
            status=MediaItem.PENDING_MODERATION,
            post_links__isnull=True
        ).prefetch_related("versions").order_by("-created")

        posts_data = PostModerationSerializer(posts_qs, many=True, context={'request': request}).data
        orphan_media_data = UnpublishedMediaItemSerializer(orphan_media_qs, many=True, context={'request': request}).data

        return Response({
            "posts": posts_data,
            "orphan_media": orphan_media_data,
        })


class ModerationActionCreateView(generics.CreateAPIView):
    """
    POST /api/moderation/action/
    Performs a moderation action on a post or media item.
    Example payload:
    {
      "entity_type": "post",
      "entity_id": 123,
      "action": "reject",
      "rejection_reason": 5,
      "comment": "Inappropriate content"
    }
    """
    serializer_class = ModerationActionCreateSerializer
    permission_classes = [IsAdminUser]