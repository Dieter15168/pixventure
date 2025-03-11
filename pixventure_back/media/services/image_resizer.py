# media/services/image_resizer.py

import io
import uuid
from PIL import Image, UnidentifiedImageError
from django.core.files.uploadedfile import InMemoryUploadedFile

def generate_resized_image(
    file_obj,
    max_size=(300, 300),
    output_format="WEBP",
    image_mode="RGB",
    quality=85
) -> InMemoryUploadedFile:
    """
    Generates a resized image from the given file object.

    :param file_obj: An image file-like object (UploadedFile or in-memory file).
    :param max_size: (width, height) tuple for the maximum size.
    :param output_format: Format for the resized image, e.g. 'WEBP', 'JPEG', etc.
    :param image_mode: Image mode to convert to (e.g. 'RGB').
    :param quality: Quality setting for the output (1-100).
    :return: An InMemoryUploadedFile representing the resized image.
    :raises ValueError: If the file is not a valid image or cannot be processed.
    """
    try:
        # Verify and re-open the image
        image = Image.open(file_obj)
        image.verify()
        file_obj.seek(0)
        image = Image.open(file_obj)

        # Convert to desired color mode, e.g. RGB
        image = image.convert(image_mode)

        # Resize
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save to in-memory file
        thumb_io = io.BytesIO()
        image.save(thumb_io, format=output_format, quality=quality)
        thumb_io.seek(0)

        # Create an InMemoryUploadedFile for Django
        resized_file = InMemoryUploadedFile(
            thumb_io,
            field_name=None,
            name=f"resized_{uuid.uuid4().hex}.{output_format.lower()}",
            content_type=f"image/{output_format.lower()}",
            size=thumb_io.getbuffer().nbytes,
            charset=None
        )

        return resized_file

    except UnidentifiedImageError:
        raise ValueError("The uploaded file is not a valid image.")
    except Exception as e:
        raise ValueError(f"An error occurred while processing the image: {e}")
