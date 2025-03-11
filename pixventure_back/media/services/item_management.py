from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from media.models import (
    MediaItem, MediaItemVersion, MediaItemHash, HashType
)
from media.services.file_metadata import compute_file_hash, get_image_info
from media.services.image_resize import generate_thumbnail

def process_uploaded_file(file_obj: UploadedFile, user):
    """
    Handles file upload processing:
    - Validates image/video files
    - Computes hash for duplicate detection
    - Saves original media & creates thumbnail for images
    """
    if file_obj.size == 0:
        return {"error": "File is empty."}

    content_type = file_obj.content_type
    is_image = content_type.startswith("image/")
    is_video = content_type.startswith("video/")

    if not is_image and not is_video:
        return {"error": f"Unsupported file type: {content_type}"}

    width = None
    height = None
    original_file_size = file_obj.size

    # If image, validate and extract dimensions
    if is_image:
        try:
            info = get_image_info(file_obj)
            width, height = info["width"], info["height"]
            original_file_size = info["file_size"]
        except ValueError as e:
            return {"error": f"Invalid image file: {e}"}

    # Compute BLAKE3 hash for deduplication
    try:
        hash_value = compute_file_hash(file_obj)
    except Exception as e:
        return {"error": f"Hash computation failed: {e}"}

    # Check for duplicates
    hash_type, _ = HashType.objects.get_or_create(name="blake3")
    if MediaItemHash.objects.filter(hash_type=hash_type, hash_value=hash_value).exists():
        return {"error": "Duplicate file detected (BLAKE3 match)."}

    with transaction.atomic():
        media_type = MediaItem.PHOTO if is_image else MediaItem.VIDEO

        media_item = MediaItem.objects.create(
            owner=user,
            media_type=media_type,
            original_filename=file_obj.name,
            status=MediaItem.PENDING_MODERATION
        )

        # Save original version
        original_version = MediaItemVersion.objects.create(
            media_item=media_item,
            version_type=MediaItemVersion.ORIGINAL,
            file=file_obj,
            width=width,
            height=height,
            file_size=original_file_size,
        )

        # Store hash for original
        MediaItemHash.objects.create(
            media_item_version=original_version,
            hash_type=hash_type,
            hash_value=hash_value
        )

        # Generate thumbnail if image
        thumbnail_version = None
        if is_image:
            try:
                thumb_file = generate_thumbnail(file_obj)
                thumb_hash = compute_file_hash(thumb_file)

                thumbnail_version = MediaItemVersion.objects.create(
                    media_item=media_item,
                    version_type=MediaItemVersion.THUMBNAIL,
                    file=thumb_file
                )

                # Extract and store thumbnail metadata
                thumb_info = get_image_info(thumb_file)
                thumbnail_version.width = thumb_info["width"]
                thumbnail_version.height = thumb_info["height"]
                thumbnail_version.file_size = thumb_info["file_size"]
                thumbnail_version.save()

                # Store hash for thumbnail
                MediaItemHash.objects.create(
                    media_item_version=thumbnail_version,
                    hash_type=hash_type,
                    hash_value=thumb_hash
                )
            except ValueError as e:
                return {"error": f"Thumbnail creation failed: {e}"}

    # Build response with media item & thumbnail URL
    resp = {"media_item_id": media_item.id}
    if thumbnail_version:
        resp["thumbnail_url"] = thumbnail_version.file.url

    return resp
