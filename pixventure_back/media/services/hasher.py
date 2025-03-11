# media/services/hasher.py

import blake3

def compute_file_hash(file_obj, hash_type="blake3"):
    """
    Compute the hash (currently defaults to BLAKE3) for a file-like object.

    :param file_obj: An UploadedFile or file-like object with .chunks() or .read()
    :param hash_type: The type of hash to compute, e.g. "blake3", "sha256", etc.
    :return: String hex digest of the hash.
    """
    if hash_type != "blake3":
        # Placeholder for future expansions to other hash types
        raise NotImplementedError(f"Hash type '{hash_type}' is not implemented.")

    hasher = blake3.blake3()

    # Some file-like objects have .chunks(), some do not. Handle both.
    try:
        for chunk in file_obj.chunks():
            hasher.update(chunk)
    except AttributeError:
        hasher.update(file_obj.read())
        file_obj.seek(0)  # Reset file pointer

    return hasher.hexdigest()
