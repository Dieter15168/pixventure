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
    APPROVED = 2
    PUBLISHED = 3
    PRIVATE = 4
    REJECTED = 5
    DELETED = 6
    ARCHIVED = 7

    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING_MODERATION, 'Pending moderation'),
        (APPROVED, 'Approved'),
        (PUBLISHED, 'Published'),
        (PRIVATE, 'Private'),
        (REJECTED, 'Rejected by moderation'),
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
    MEDIA_TYPE_CHOICES = [
        (PHOTO, 'Photo'),
        (VIDEO, 'Video'),
    ]

    media_type = models.IntegerField(choices=MEDIA_TYPE_CHOICES)

    # Basic naming / metadata
    original_filename = models.CharField(max_length=256, null=True, blank=True)

    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='media_items'
    )

    # Simple likes counter
    likes_counter = models.IntegerField(default=0)
    
    # Blurred items will be blurred for non-paying users
    is_blurred = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id} (Type: {self.get_media_type_display()})"
    

class MediaItemVersion(models.Model):
    """
    Represents a specific version of a media item (e.g., thumbnail, preview, watermarked).
    Each version has its own file reference and metadata like dimensions and file size.
    """
    # Automatic timestamps for creation and update
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    # Versions
    ORIGINAL = 0
    THUMBNAIL = 1
    PREVIEW = 2
    BLURRED_THUMBNAIL = 3
    BLURRED_PREVIEW = 4
    WATERMARKED = 5
    
    VERSION_CHOICES = [
        (ORIGINAL, 'Original'),
        (THUMBNAIL, 'Thumbnail'),
        (PREVIEW, 'Preview'),
        (BLURRED_THUMBNAIL, 'Blurred Thumbnail'),
        (BLURRED_PREVIEW, 'Blurred Preview'),
        (WATERMARKED, 'Watermarked'),
    ]

    version_type = models.IntegerField(choices=VERSION_CHOICES)
    media_item = models.ForeignKey(MediaItem, on_delete=models.CASCADE, related_name='versions')

    # File reference for this version
    file = models.FileField(upload_to='media_versions/', null=True, blank=True)

    # Metadata specific to this version
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Whether the file has been renamed for SEO or other reasons
    is_renamed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_version_type_display()} version of MediaItem {self.media_item.id}"


class HashType(models.Model):
    """
    Represents a type of hash used for content recognition (e.g., sha256, p-hash).
    """
    # Automatic timestamps for creation and update
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class MediaItemHash(models.Model):
    """
    Stores hash values for a given MediaItem version, with references to the HashType.
    """
    # Automatic timestamps for creation and update
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    media_item_version = models.ForeignKey(MediaItemVersion, on_delete=models.CASCADE, related_name='hashes')
    hash_type = models.ForeignKey(HashType, null=True, on_delete=models.CASCADE, related_name='hashes')
    hash_value = models.CharField(null=True, max_length=64)

    def __str__(self):
        return f"Hash ({self.hash_type.name}) for MediaItemVersion {self.media_item_version.id}"