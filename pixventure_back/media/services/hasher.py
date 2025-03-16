# media/services/hasher.py

import blake3
import imagehash
from media.utils.image_loader import open_image

def compute_file_hash(file_obj, hash_type="blake3"):
    """
    Compute a hash (defaults to BLAKE3) for a file-like object.
    """
    if hash_type != "blake3":
        raise NotImplementedError(f"Hash type '{hash_type}' is not implemented in compute_file_hash.")
    
    hasher = blake3.blake3()
    try:
        for chunk in file_obj.chunks():
            hasher.update(chunk)
    except AttributeError:
        hasher.update(file_obj.read())
        file_obj.seek(0)
    
    return hasher.hexdigest()

def compute_fuzzy_hash(file_obj, hash_type="phash"):
    """
    Compute a fuzzy (perceptual) hash for an image.
    
    :param file_obj: A file-like object containing image data.
    :param hash_type: Type of perceptual hash to compute (defaults to 'phash').
    :return: String representation of the computed hash.
    """
    try:
        image = open_image(file_obj).convert("RGB")
    except Exception as e:
        raise ValueError(f"Cannot open image for fuzzy hash: {e}")
    
    if hash_type == "phash":
        # Compute perceptual hash using DCT (phash)
        return str(imagehash.phash(image))
    else:
        raise NotImplementedError(f"Fuzzy hash type '{hash_type}' is not implemented.")