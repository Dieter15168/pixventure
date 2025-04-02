import os
import uuid
from django.db import models
from django.contrib.auth.models import User


def media_version_upload_to(instance, filename):
    """
    Generates a dynamic upload path for MediaItemVersion files.
    
    For the ORIGINAL version, a generic filename is generated (e.g. original_<uuid>.<ext>).
    For other versions, files are stored in version-specific folders.
    """
    # Mapping from version type to folder name.
    folder_map = {
        MediaItemVersion.ORIGINAL: 'original',
        MediaItemVersion.THUMBNAIL: 'thumbnail',
        MediaItemVersion.PREVIEW: 'preview',
        MediaItemVersion.BLURRED_THUMBNAIL: 'blurred_thumbnail',
        MediaItemVersion.BLURRED_PREVIEW: 'blurred_preview',
        MediaItemVersion.WATERMARKED: 'watermarked',
    }
    folder = folder_map.get(instance.version_type, 'media_versions')
    
    # Extract the extension from the original filename.
    ext = os.path.splitext(filename)[1].lower()  # e.g. ".jpg"
    
    # For the ORIGINAL version, use a generic filename.
    if instance.version_type == MediaItemVersion.ORIGINAL:
        new_filename = f"original_{uuid.uuid4().hex}{ext}"
    else:
        new_filename = f"{folder}_{uuid.uuid4().hex}{ext}"
    
    return os.path.join(folder, new_filename)


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
    media_item = models.ForeignKey('MediaItem', on_delete=models.CASCADE, related_name='versions')

    # File reference for this version using the custom upload_to callable.
    file = models.FileField(upload_to=media_version_upload_to, null=True, blank=True)

    # Metadata specific to this version
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # For videos only – store duration in seconds.
    video_duration = models.FloatField(null=True, blank=True)
    
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
    

class DuplicateCase(models.Model):
    """
    Represents a detected duplicate between a candidate media item and an existing duplicate media item.
    Each record is created per candidate-duplicate pair and includes a confidence score.
    """
    PENDING = 0
    CONFIRMED = 1
    FALSE_POSITIVE = 2

    STATUS_CHOICES = [
        (PENDING, 'Pending Review'),
        (CONFIRMED, 'Confirmed Duplicate'),
        (FALSE_POSITIVE, 'False Positive'),
    ]

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    candidate = models.ForeignKey(MediaItem, on_delete=models.CASCADE, related_name='duplicate_candidates')
    duplicate = models.ForeignKey(MediaItem, on_delete=models.CASCADE, related_name='duplicate_matches')
    confidence_score = models.FloatField(default=1.0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f"DuplicateCase: Candidate {self.candidate.id} vs Duplicate {self.duplicate.id} ({self.get_status_display()})"