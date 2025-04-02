# moderation/views.py

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import ValidationError
from posts.models import Post
from media.models import MediaItem, DuplicateCluster
from .models import RejectionReason
from .serializers import PostModerationSerializer, ModerationActionCreateSerializer, RejectionReasonSerializer, DuplicateClusterModerationSerializer
from media.serializers import UnpublishedMediaItemSerializer
from moderation.managers import ModerationManager

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
        
        # Fetch duplicate clusters
        clusters = DuplicateCluster.objects.filter(status=DuplicateCluster.PENDING).prefetch_related('items__versions')
        clusters_data = DuplicateClusterModerationSerializer(clusters, many=True, context={'request': request}).data

        return Response({
            "posts": posts_data,
            "orphan_media": orphan_media_data,
            "duplicate_clusters": clusters_data,
        })


class ModerationActionCreateView(generics.CreateAPIView):
    """
    API view for creating moderation actions on posts or media items.
    
    POST /api/moderation/action/
    
    Expected payload:
    {
      "entity_type": "post",
      "entity_id": 123,
      "action": "reject",
      "rejection_reason": [5],
      "comment": "Inappropriate content"
    }
    """
    serializer_class = ModerationActionCreateSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        """
        Handles the creation of a moderation action by delegating to the ModerationManager.
        """
        validated_data = serializer.validated_data
        moderator = self.request.user
        entity_type = validated_data['entity_type']
        entity_id = validated_data['entity_id']
        action = validated_data['action']
        comment = validated_data.get('comment', "")
        rejection_reasons = validated_data.get('rejection_reason', [])
        is_featured_post = validated_data.get('is_featured_post', False)

        manager = ModerationManager()

        if action == 'approve':
            if entity_type == 'post':
                mod_action = manager.handle_post_approval(entity_id, moderator, comment, is_featured_post)
            elif entity_type == 'media':
                mod_action = manager.handle_item_approval(entity_id, moderator, comment)
            else:
                raise ValidationError("Invalid entity type for approval.")
        elif action == 'reject':
            if entity_type == 'post':
                mod_action = manager.handle_post_rejection(entity_id, moderator, rejection_reasons, comment)
            elif entity_type == 'media':
                mod_action = manager.handle_item_rejection(entity_id, moderator, rejection_reasons, comment)
            else:
                raise ValidationError("Invalid entity type for rejection.")
        else:
            raise ValidationError("Invalid moderation action.")

        serializer.instance = mod_action
        return mod_action

    def create(self, request, *args, **kwargs):
        """
        Overridden create method to process the moderation action and return a response.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mod_action = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.to_representation(mod_action), status=status.HTTP_201_CREATED, headers=headers)


class ActiveRejectionReasonListView(generics.ListAPIView):
    """
    Returns a list of active rejection reasons.
    Only available to admin users.
    """
    serializer_class = RejectionReasonSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None
    queryset = RejectionReason.objects.filter(is_active=True).order_by('order')
    
    
class DuplicateClusterListView(generics.ListAPIView):
    """
    Returns all duplicate clusters that are Pending (or whichever filter you choose).
    Only accessible to admin users.
    """
    serializer_class = DuplicateClusterModerationSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return DuplicateCluster.objects.filter(
            status=DuplicateCluster.PENDING
        ).prefetch_related('items__versions', 'hash_type')