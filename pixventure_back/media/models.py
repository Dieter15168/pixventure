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
    
    
def _is_better_than(candidate: MediaItem, incumbent: MediaItem) -> bool:
    """
    Returns True if candidate is "better" than incumbent by:
      1) Higher resolution (width x height),
      2) If resolution ties, bigger file size.
    """
    # We assume 'best' means highest total pixels. If items have multiple versions,
    # we need to figure out which version to compare. Let's assume the original version.
    cand_original = candidate.versions.filter(version_type=MediaItemVersion.ORIGINAL).first()
    inc_original = incumbent.versions.filter(version_type=MediaItemVersion.ORIGINAL).first()

    # If either doesn't exist or data is missing, default to false or fallback logic
    if not cand_original or not inc_original:
        return False

    cand_pixels = (cand_original.width or 0) * (cand_original.height or 0)
    inc_pixels = (inc_original.width or 0) * (inc_original.height or 0)

    if cand_pixels > inc_pixels:
        return True
    elif cand_pixels < inc_pixels:
        return False
    else:
        # If pixel count is the same, fallback to file size.
        cand_size = cand_original.file_size or 0
        inc_size = inc_original.file_size or 0
        return cand_size > inc_size

class DuplicateCluster(models.Model):
    PENDING = 0
    CONFIRMED = 1
    IGNORED = 2

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (IGNORED, 'Ignored'),
    ]

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    hash_type = models.ForeignKey(
        HashType, on_delete=models.CASCADE, related_name='clusters'
    )
    hash_value = models.CharField(max_length=64)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)

    items = models.ManyToManyField(
        MediaItem,
        related_name='duplicate_clusters'
    )

    best_item = models.ForeignKey(
        MediaItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='best_in_clusters'
    )

    class Meta:
        unique_together = ('hash_type', 'hash_value')
        verbose_name = "Duplicate Cluster"
        verbose_name_plural = "Duplicate Clusters"

    def __str__(self):
        return f"Cluster {self.id} - {self.hash_type.name}:{self.hash_value}"

    def update_best_item(self):
        """
        Always re-evaluates which item in this cluster is 'best' according to:
        1. Higher resolution (width * height)
        2. If resolution ties, prefer larger file size.
        """
        if not self.items.exists():
            self.best_item = None
            self.save()
            return

        best_item = None
        for item in self.items.all():
            if best_item is None or _is_better_than(item, best_item):
                best_item = item

        self.best_item = best_item
        self.save()