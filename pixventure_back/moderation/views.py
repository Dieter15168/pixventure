# moderation/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.shortcuts import get_object_or_404

from posts.models import Post
from media.models import MediaItem
from .models import ModerationAction, RejectionReason
#from .serializers import ModerationActionSerializer  # define if needed

class ModerationActionView(APIView):
    """
    An endpoint for performing a moderation action on either a Post or a MediaItem.
    POST:
      body: {
        "entity_type": "post"|"media",
        "entity_id": <int>,
        "new_status": <int>,   # e.g. 2=Published, 3=Rejected
        "rejection_reason_id": <int or null>,
        "comment": "optional text"
      }
    """
    permission_classes = [IsAdminUser]  # only admin can moderate

    def post(self, request):
        entity_type = request.data.get('entity_type')
        entity_id = request.data.get('entity_id')
        new_status = request.data.get('new_status')
        rejection_reason_id = request.data.get('rejection_reason_id')
        comment = request.data.get('comment', '')

        if not entity_type or not entity_id:
            return Response({"detail": "entity_type and entity_id are required."}, status=400)

        # 1. Load the entity
        if entity_type == 'post':
            post = get_object_or_404(Post, pk=entity_id)
            old_status = post.status
            # update post status
            post.status = new_status
            post.save()

            # create ModerationAction
            action = ModerationAction(
                post=post,
                old_status=old_status,
                new_status=new_status,
                owner=post.owner if post.owner else None,
                moderator=request.user,
                comment=comment
            )
        elif entity_type == 'media':
            media_item = get_object_or_404(MediaItem, pk=entity_id)
            old_status = media_item.status
            # update media status
            media_item.status = new_status
            media_item.save()

            action = ModerationAction(
                media_item=media_item,
                old_status=old_status,
                new_status=new_status,
                owner=media_item.owner if media_item.owner else None,
                moderator=request.user,
                comment=comment
            )
        else:
            return Response({"detail": "Invalid entity_type. Must be 'post' or 'media'."}, status=400)

        # 2. Set rejection reason if provided
        if rejection_reason_id:
            reason = get_object_or_404(RejectionReason, pk=rejection_reason_id)
            action.rejection_reason = reason

        action.save()

        return Response({"detail": "Moderation action completed successfully."}, status=200)
