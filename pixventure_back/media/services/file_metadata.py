import blake3
import io
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError

def compute_file_hash(file_obj, hash_name="blake3"):
    """
    Compute a BLAKE3 (or other) hash for the file_obj.
    file_obj can be an UploadedFile or an in-memory file-like.
    """
    hasher = blake3.blake3()
    try:
        for chunk in file_obj.chunks():
            hasher.update(chunk)
    except AttributeError:
        # Fall back to reading the file fully if `.chunks()` is not available
        hasher.update(file_obj.read())
        file_obj.seek(0)  # Reset file pointer

    return hasher.hexdigest()

def get_image_info(file_obj: UploadedFile) -> dict:
    """
    Use Pillow to open and validate the image.
    Return a dict: {width, height, file_size, format}
    Raises an IOError if it's not a valid image.
    """
    # Read file into memory safely
    content = io.BytesIO()
    
    try:
        for chunk in file_obj.chunks():
            content.write(chunk)
    except AttributeError:
        # If `.chunks()` is unavailable, fall back to reading full content
        content.write(file_obj.read())

    content.seek(0)  # Reset pointer

    try:
        im = Image.open(content)
        im.verify()  # Validate image file
        content.seek(0)  # Reset for re-opening
        im = Image.open(content)  # Re-open to extract metadata
        im = im.convert("RGB")  # Ensure image is in RGB mode (avoiding P mode issues)

        return {
            "width": im.width,
            "height": im.height,
            "file_size": content.getbuffer().nbytes,
            "format": im.format,  # 'JPEG', 'PNG', 'WEBP', etc.
        }
    
    except UnidentifiedImageError:
        raise IOError("The uploaded file is not a valid image.")
    except Exception as e:
        raise IOError(f"Error processing image: {e}")
