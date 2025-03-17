"""
Managers for handling moderation logic.
Provides business logic for post and media item moderation.
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from posts.models import Post
from media.models import MediaItem
from moderation.models import ModerationAction, RejectionReason

class ModerationManager:
    """
    Handles moderation actions for posts and media items.
    Provides methods for approving and rejecting posts and media items.
    """

    @transaction.atomic
    def handle_post_approval(self, post_id, moderator, comment=""):
        """
        Approves a post.

        Args:
            post_id (int): ID of the post to approve.
            moderator (User): The moderator performing the action.
            comment (str): Optional comment for the action.

        Returns:
            ModerationAction: The created moderation action record.
        """
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise ValidationError("Post not found.")

        old_status = post.status
        post.status = Post.APPROVED  # Using the constant defined in the Post model.
        post.save()

        mod_action = ModerationAction.objects.create(
            post=post,
            old_status=old_status,
            new_status=Post.APPROVED,
            owner=post.owner,
            moderator=moderator,
            comment=comment,
        )
        return mod_action

    @transaction.atomic
    def handle_item_approval(self, media_item_id, moderator, comment=""):
        """
        Approves a media item.

        Args:
            media_item_id (int): ID of the media item to approve.
            moderator (User): The moderator performing the action.
            comment (str): Optional comment for the action.

        Returns:
            ModerationAction: The created moderation action record.
        """
        try:
            media_item = MediaItem.objects.get(id=media_item_id)
        except MediaItem.DoesNotExist:
            raise ValidationError("Media item not found.")

        old_status = media_item.status
        media_item.status = MediaItem.APPROVED  # Using the constant defined in the MediaItem model.
        media_item.save()

        mod_action = ModerationAction.objects.create(
            media_item=media_item,
            old_status=old_status,
            new_status=MediaItem.APPROVED,
            owner=media_item.owner,
            moderator=moderator,
            comment=comment,
        )
        return mod_action

    @transaction.atomic
    def handle_post_rejection(self, post_id, moderator, rejection_reason_ids, comment=""):
        """
        Rejects a post.

        Args:
            post_id (int): ID of the post to reject.
            moderator (User): The moderator performing the action.
            rejection_reason_ids (list): List of IDs of active rejection reasons.
            comment (str): Optional comment for the action.

        Returns:
            ModerationAction: The created moderation action record.
        """
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise ValidationError("Post not found.")

        if not rejection_reason_ids:
            raise ValidationError("At least one rejection reason is required for rejection.")

        reasons = list(RejectionReason.objects.filter(id__in=rejection_reason_ids, is_active=True))
        if len(reasons) != len(rejection_reason_ids):
            raise ValidationError("One or more rejection reasons are invalid or inactive.")

        old_status = post.status
        post.status = Post.REJECTED  # Using the constant defined in the Post model.
        post.save()

        mod_action = ModerationAction.objects.create(
            post=post,
            old_status=old_status,
            new_status=Post.REJECTED,
            owner=post.owner,
            moderator=moderator,
            comment=comment,
        )
        mod_action.rejection_reasons.add(*reasons)
        return mod_action

    @transaction.atomic
    def handle_item_rejection(self, media_item_id, moderator, rejection_reason_ids, comment=""):
        """
        Rejects a media item.

        Args:
            media_item_id (int): ID of the media item to reject.
            moderator (User): The moderator performing the action.
            rejection_reason_ids (list): List of IDs of active rejection reasons.
            comment (str): Optional comment for the action.

        Returns:
            ModerationAction: The created moderation action record.
        """
        try:
            media_item = MediaItem.objects.get(id=media_item_id)
        except MediaItem.DoesNotExist:
            raise ValidationError("Media item not found.")

        if not rejection_reason_ids:
            raise ValidationError("At least one rejection reason is required for rejection.")

        reasons = list(RejectionReason.objects.filter(id__in=rejection_reason_ids, is_active=True))
        if len(reasons) != len(rejection_reason_ids):
            raise ValidationError("One or more rejection reasons are invalid or inactive.")

        old_status = media_item.status
        media_item.status = MediaItem.REJECTED  # Using the constant defined in the MediaItem model.
        media_item.save()

        mod_action = ModerationAction.objects.create(
            media_item=media_item,
            old_status=old_status,
            new_status=MediaItem.REJECTED,
            owner=media_item.owner,
            moderator=moderator,
            comment=comment,
        )
        mod_action.rejection_reasons.add(*reasons)
        return mod_action
