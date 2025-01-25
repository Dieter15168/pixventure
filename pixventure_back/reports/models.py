from django.db import models
from django.conf import settings
from django.utils import timezone

from posts.models import Post
from media.models import MediaItem
from moderation.models import ModerationAction

class ReportReason(models.Model):
    """
    Reasons for reporting content (e.g., 'spam', 'harassment', 'nudity', etc.).
    Includes an 'order' field for UI ordering and 'is_active' for soft deletes.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"[{self.order}] {self.name} (Active: {self.is_active})"


class Report(models.Model):
    """
    A user report about a piece of content (Post or MediaItem).
    Fields:
      - user or anonymous_email
      - reason
      - user_comment (reporter's comment)
      - moderator_comment (staff response)
      - status: pending => 0, rejected => 1, satisfied => 2
      - references to post or media
      - link to a possible ModerationAction if it triggered one
      - opened_at (creation date), closed_at (when resolved)
    """
    PENDING = 0
    REJECTED = 1
    SATISFIED = 2

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (REJECTED, 'Rejected'),
        (SATISFIED, 'Satisfied'),
    ]

    # Optional references to the content
    post = models.ForeignKey(Post, null=True, blank=True,
                             on_delete=models.CASCADE, related_name='reports')
    media_item = models.ForeignKey(MediaItem, null=True, blank=True,
                                   on_delete=models.CASCADE, related_name='reports')

    # The user who created the report (or None if anonymous)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='reports_submitted'
    )
    # If anonymous, we can store a custom email if user wants notifications
    anonymous_email = models.EmailField(null=True, blank=True)

    reason = models.ForeignKey(
        'ReportReason',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='reports'
    )
    user_comment = models.TextField(null=True, blank=True, help_text="Reporter comment")
    moderator_comment = models.TextField(null=True, blank=True, help_text="Admin note")

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # Optionally link to a moderation action if the admin took an action on the item
    moderation_action = models.ForeignKey(
        'moderation.ModerationAction',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='reports'
    )

    def __str__(self):
        entity_label = (
            f"Post {self.post_id}" if self.post
            else f"Media {self.media_item_id}" if self.media_item
            else "Unknown content"
        )
        return f"Report {self.id} on {entity_label} - Status: {self.get_status_display()}"

    def mark_resolved(self, new_status, moderator_comment=None):
        """
        Helper method to finalize the report with a new status (REJECTED or SATISFIED),
        set closed_at, and optionally add a moderator comment.
        """
        self.status = new_status
        self.closed_at = timezone.now()
        if moderator_comment is not None:
            self.moderator_comment = moderator_comment
        self.save()