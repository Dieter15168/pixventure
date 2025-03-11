# media/services/media_version_creator.py

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from media.models import MediaItem, MediaItemVersion, MediaItemHash, HashType
from media.services.hasher import compute_file_hash
from media.services.image_metadata import extract_image_metadata

def create_media_item_version(
    media_item: MediaItem,
    file_obj: UploadedFile,
    version_type: int,
    hash_type_name: str = "blake3",
    existing_hash_value: str = None,
    is_image: bool = False
) -> MediaItemVersion:
    """
    Creates a MediaItemVersion record for the given MediaItem.

    :param media_item: MediaItem instance to which this version belongs
    :param file_obj: The file object to be stored in this version
    :param version_type: One of MediaItemVersion's version-type constants
    :param hash_type_name: The name of the hash type to store (default 'blake3')
    :param existing_hash_value: Optionally pass in a pre-computed hash to avoid re-hashing
    :param is_image: Boolean indicating if the file is an image (for metadata extraction)
    :return: The created MediaItemVersion instance.
    """
    with transaction.atomic():
        # Create the version entry
        version = MediaItemVersion.objects.create(
            media_item=media_item,
            version_type=version_type,
            file=file_obj
        )

        # Extract metadata if this is an image
        if is_image:
            try:
                meta = extract_image_metadata(file_obj)
                version.width = meta["width"]
                version.height = meta["height"]
                version.file_size = meta["file_size"]
            except Exception:
                # Depending on your policy, you might raise or just ignore
                raise ValueError("Could not extract image metadata.")
        else:
            # For non-image, we at least store file size
            version.file_size = file_obj.size

        version.save()

        # Compute (or store) hash
        if existing_hash_value:
            hash_value = existing_hash_value
        else:
            hash_value = compute_file_hash(file_obj, hash_type=hash_type_name)

        hash_type_obj, _ = HashType.objects.get_or_create(name=hash_type_name)
        MediaItemHash.objects.create(
            media_item_version=version,
            hash_type=hash_type_obj,
            hash_value=hash_value
        )

    return version
