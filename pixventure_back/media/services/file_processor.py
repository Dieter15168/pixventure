# media/services/file_processor.py

from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError

from media.models import MediaItem, MediaItemVersion, HashType, MediaItemHash
from media.services.hasher import compute_file_hash
from media.services.image_metadata import extract_image_metadata
from media.services.image_resizer import generate_resized_image
from media.services.media_version_creator import create_media_item_version

def process_uploaded_file(file_obj: UploadedFile, user):
    """
    Main orchestrator for handling file uploads:
    - Validates the incoming file (image or video).
    - Checks duplicates via BLAKE3 hash.
    - Creates a new MediaItem in the database.
    - Creates the "original" version of the file.
    - If the file is an image, generates a thumbnail version.
    
    Returns a dict with success info or an error message.
    """
    # 1. Basic file validation
    if file_obj.size == 0:
        return {"error": "File is empty."}

    content_type = file_obj.content_type
    is_image = content_type.startswith("image/")
    is_video = content_type.startswith("video/")

    if not is_image and not is_video:
        return {"error": f"Unsupported file type: {content_type}"}

    # 2. Optional: if image, extract dimensions/metadata for validation
    #    You can do it here or wait until the creation of the version.
    width, height = None, None
    if is_image:
        try:
            meta = extract_image_metadata(file_obj)
            width, height = meta["width"], meta["height"]
            # We won't store in DB here; we'll do that in create_media_item_version.
            # But you could do extra validation if needed (e.g., max dimension checks).
        except Exception as e:
            return {"error": f"Invalid image file: {e}"}
        finally:
            # Seek back to start for further usage
            file_obj.seek(0)

    # 3. Compute BLAKE3 hash for deduplication
    try:
        hash_value = compute_file_hash(file_obj, hash_type="blake3")
        file_obj.seek(0)
    except Exception as e:
        return {"error": f"Hash computation failed: {e}"}

    # 4. Check for duplicates
    hash_type_obj, _ = HashType.objects.get_or_create(name="blake3")
    if MediaItemHash.objects.filter(hash_type=hash_type_obj, hash_value=hash_value).exists():
        return {"error": "Duplicate file detected (BLAKE3 match)."}

    # 5. Create the MediaItem and the Original version
    with transaction.atomic():
        media_type = MediaItem.PHOTO if is_image else MediaItem.VIDEO
        media_item = MediaItem.objects.create(
            owner=user,
            media_type=media_type,
            original_filename=file_obj.name,
            status=MediaItem.PENDING_MODERATION
        )

        original_version = create_media_item_version(
            media_item=media_item,
            file_obj=file_obj,
            version_type=MediaItemVersion.ORIGINAL,
            hash_type_name="blake3",
            existing_hash_value=hash_value,
            is_image=is_image
        )

        thumbnail_version = None

        # 6. If it's an image, generate a thumbnail
        if is_image:
            try:
                resized_file = generate_resized_image(file_obj)  # defaults to max 300x300
                thumbnail_version = create_media_item_version(
                    media_item=media_item,
                    file_obj=resized_file,
                    version_type=MediaItemVersion.THUMBNAIL,
                    hash_type_name="blake3",
                    # We could let the function compute a new hash, or we can compute it ourselves
                    # existing_hash_value=some_hash
                    is_image=True
                )
            except ValueError as e:
                return {"error": f"Thumbnail creation failed: {e}"}

    # 7. Build response
    resp = {"media_item_id": media_item.id}
    if thumbnail_version:
        resp["thumbnail_url"] = thumbnail_version.file.url

    return resp
