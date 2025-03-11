# media/services/image_metadata.py

import io
from PIL import Image, UnidentifiedImageError

def extract_image_metadata(file_obj) -> dict:
    """
    Uses Pillow to open and validate the image, returning basic metadata.
    :param file_obj: A file-like object (UploadedFile or in-memory).
    :return: A dict with keys: 'width', 'height', 'file_size', 'format'
    :raises IOError: If it's not a valid image or can't be processed.
    """
    content = io.BytesIO()
    try:
        for chunk in file_obj.chunks():
            content.write(chunk)
    except AttributeError:
        # Fall back for objects without .chunks()
        content.write(file_obj.read())

    content.seek(0)

    try:
        im = Image.open(content)
        im.verify()  # validate
        content.seek(0)
        im = Image.open(content)
        im = im.convert("RGB")

        return {
            "width": im.width,
            "height": im.height,
            "file_size": content.getbuffer().nbytes,
            "format": im.format,
        }

    except UnidentifiedImageError:
        raise IOError("The uploaded file is not a valid image.")
    except Exception as e:
        raise IOError(f"Error processing image: {e}")
