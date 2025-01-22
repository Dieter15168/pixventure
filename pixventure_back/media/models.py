from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class MediaItem(models.Model):
    """
    Represents a piece of media (photo or video) uploaded by users.
    Stores file references, metadata, and status tracking.
    """

    # Automatic timestamps for creation and update
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # Lifecycle statuses
    DRAFT = 0
    PENDING_MODERATION = 1
    PUBLISHED = 2
    DELETED = 3
    ARCHIVED = 4

    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING_MODERATION, 'Pending moderation'),
        (PUBLISHED, 'Published'),
        (DELETED, 'Deleted'),
        (ARCHIVED, 'Archived'),
    ]

    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=PENDING_MODERATION,
        null=False,
        blank=False
    )

    # Media type (photo or video)
    PHOTO = 1
    VIDEO = 2
    ITEM_TYPE_CHOICES = [
        (PHOTO, 'Photo'),
        (VIDEO, 'Video'),
    ]

    item_type = models.IntegerField(choices=ITEM_TYPE_CHOICES)

    # Basic naming / metadata
    original_filename = models.CharField(max_length=256, null=True, blank=True)
    file_format = models.CharField(max_length=4)  # e.g., "jpg", "png", "mp4"

    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='media_items'
    )

    # File references: ideally stored on object storage (e.g., S3).
    original_file = models.FileField(upload_to='original', null=True, blank=True)
    watermarked_file = models.FileField(upload_to='watermarked', null=True, blank=True)
    preview_file = models.FileField(upload_to='preview', null=True, blank=True)
    blurred_preview_file = models.FileField(upload_to='blurred_preview', null=True, blank=True)
    thumbnail_file = models.FileField(upload_to='thumbnail', null=True, blank=True)
    blurred_thumbnail_file = models.FileField(upload_to='blurred_thumbnail', null=True, blank=True)

    # Dimensions and size
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # Use BigInteger if >2GB possible

    # Whether the file has been renamed for SEO or other reasons
    is_renamed = models.BooleanField(default=False)

    # Simple likes counter
    likes_counter = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.id} (Type: {self.get_item_type_display()})"



class MediaItemHash(models.Model):
    """
    Stores hash values for a given MediaItem (e.g., sha256, p-hash, etc.),
    useful for duplicate detection or content recognition.
    """
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE, related_name='hashes')
    sha256 = models.CharField(max_length=64, null=True, blank=True)
    a_hash = models.CharField(max_length=64, null=True, blank=True)
    p_hash = models.CharField(max_length=64, null=True, blank=True)
    d_hash = models.CharField(max_length=64, null=True, blank=True)
    w_hash = models.CharField(max_length=64, null=True, blank=True)
    crop_resistant_hash = models.CharField(max_length=170, null=True, blank=True)
    color_hash = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f"Hashes for: {self.media_item}"