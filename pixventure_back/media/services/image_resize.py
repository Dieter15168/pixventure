import io
import uuid
from PIL import Image, UnidentifiedImageError
from django.core.files.uploadedfile import InMemoryUploadedFile

def generate_thumbnail(file_obj, max_size=(300, 300), output_format="WEBP") -> InMemoryUploadedFile:
    """
    Generates a thumbnail for the given image file.

    Args:
        file_obj: A file-like object containing the image.
        max_size (tuple): The maximum width and height of the thumbnail.
        output_format (str): The format for the thumbnail (e.g., "WEBP").

    Returns:
        InMemoryUploadedFile: The generated thumbnail file.

    Raises:
        ValueError: If the file is not a valid image or cannot be processed.
    """
    try:
        # Attempt to open the image file
        image = Image.open(file_obj)
        image.verify()  # Verify that it's a valid image
        image = Image.open(file_obj)  # Re-open after verify()
        image = image.convert("RGB")  # Ensure image is in RGB mode

        # Create thumbnail
        image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save thumbnail to in-memory file
        thumb_io = io.BytesIO()
        image.save(thumb_io, format=output_format, quality=85)
        thumb_io.seek(0)

        # Construct InMemoryUploadedFile
        thumb_file = InMemoryUploadedFile(
            thumb_io,
            field_name=None,
            name=f"thumb_{uuid.uuid4().hex}.{output_format.lower()}",
            content_type=f"image/{output_format.lower()}",
            size=thumb_io.getbuffer().nbytes,
            charset=None
        )

        return thumb_file

    except UnidentifiedImageError:
        raise ValueError("The uploaded file is not a valid image.")
    except Exception as e:
        raise ValueError(f"An error occurred while processing the image: {e}")
