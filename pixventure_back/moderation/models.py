from django.db import models
from django.conf import settings
from posts.models import Post
from media.models import MediaItem

class RejectionReason(models.Model):
    """
    Stores possible reasons for rejecting a Post or MediaItem.
    The `order` field controls how these reasons might be sorted in a UI.
    The `is_active` field controls whether rejection reason will be displayed in the UI.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.order}. {self.name}"
    
    class Meta:
        ordering = ['order']

class ModerationAction(models.Model):
    """
    Stores a record of moderation actions performed on either a Post or a MediaItem.
    """

    # Separate optional FKs for Post or MediaItem
    post = models.ForeignKey(
        Post,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='moderation_actions'
    )
    media_item = models.ForeignKey(
        MediaItem,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='moderation_actions'
    )
    old_status = models.IntegerField(null=True, blank=True)
    new_status = models.IntegerField(null=True, blank=True)

    # The user who owns the content
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='content_moderation_history'
    )

    # The staff/admin who performed the moderation
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='moderation_actions_performed'
    )

    # Replace single FK with a ManyToManyField for multiple reasons:
    rejection_reasons = models.ManyToManyField(RejectionReason, blank=True, related_name='moderation_actions')
    comment = models.TextField(null=True, blank=True, help_text="Optional moderator comment")

    performed_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        entity_label = (
            f"Post {self.post_id}" if self.post
            else f"Media {self.media_item_id}" if self.media_item
            else "Unknown content"
        )
        return f"[{self.performed_at}] Moderation on {entity_label}: {self.old_status} -> {self.new_status}"