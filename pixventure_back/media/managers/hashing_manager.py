# media/managers/hashing_manager.py
from media.models import MediaItemVersion, MediaItemHash, HashType
from media.services.hasher import compute_fuzzy_hash

class HashingManager:
    """
    Manager to handle computing and storing fuzzy hashes for media item versions.
    """
    
    @staticmethod
    def process_fuzzy_hash(media_item_version_id, hash_type="phash"):
        """
        Compute the fuzzy hash for a given MediaItemVersion and store it.
        
        :param media_item_version_id: ID of the MediaItemVersion.
        :param hash_type: Type of hash to compute, defaulting to 'phash'.
        """
        from media.models import MediaItemVersion  # Import here to avoid circular dependency issues.
        
        try:
            version = MediaItemVersion.objects.get(id=media_item_version_id)
        except MediaItemVersion.DoesNotExist:
            raise ValueError(f"MediaItemVersion with ID {media_item_version_id} does not exist.")
        
        # Open the file associated with this version.
        file_obj = version.file
        hash_value = compute_fuzzy_hash(file_obj, hash_type=hash_type)
        
        # Get or create the hash type record.
        hash_type_obj, _ = HashType.objects.get_or_create(name=hash_type)
        
        # Save the computed fuzzy hash.
        MediaItemHash.objects.update_or_create(
            media_item_version=version,
            hash_type=hash_type_obj,
            defaults={"hash_value": hash_value}
        )
        
        return hash_value
