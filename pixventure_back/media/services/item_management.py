# media/services/item_management.py

import blake3
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from media.models import MediaItem, MediaItemVersion, MediaItemHash, HashType

def process_uploaded_file(file_obj: UploadedFile, user):
    """
    1. Validate basic file properties (size, type).
    2. Compute BLAKE3 hash, check for duplicates.
    3. Create a MediaItem + MediaItemVersion with status = PENDING_MODERATION.
    4. Return a dict with either an error or the newly created media_item.
    """
    # Basic validation
    if file_obj.size == 0:
        return {"error": "Empty file."}
    if not file_obj.content_type.startswith("image/") and not file_obj.content_type.startswith("video/"):
        return {"error": f"Unsupported file type: {file_obj.content_type}"}

    # Hash check
    hasher = blake3.blake3()
    for chunk in file_obj.chunks():
        hasher.update(chunk)
    hash_value = hasher.hexdigest()

    hash_type, _ = HashType.objects.get_or_create(name="blake3")
    existing = MediaItemHash.objects.filter(hash_type=hash_type, hash_value=hash_value)
    if existing.exists():
        return {"error": "Duplicate file detected (blake3 match)."}

    # Create in a transaction
    with transaction.atomic():
        if file_obj.content_type.startswith("image/"):
            media_type = MediaItem.PHOTO
        else:
            media_type = MediaItem.VIDEO
        
        media_item = MediaItem.objects.create(
            owner=user,
            media_type=media_type,
            original_filename=file_obj.name,
            status=MediaItem.PENDING_MODERATION,
        )
        
        version = MediaItemVersion.objects.create(
            media_item=media_item,
            version_type=MediaItemVersion.ORIGINAL,
            file=file_obj,
        )

        MediaItemHash.objects.create(
            media_item_version=version,
            hash_type=hash_type,
            hash_value=hash_value
        )
    
    return {"media_item": media_item}
