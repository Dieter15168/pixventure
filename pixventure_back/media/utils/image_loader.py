# media/utils/image_loader.py
import os
from PIL import Image
import pyheif

def open_image(file_obj):
    """
    Opens an image from a file-like object.
    
    - If the file is HEIC/HEIF (detected by filename or header signature), reads all bytes
      and passes them to pyheif to decode the image.
    - Otherwise, uses Pillow's Image.open().
    
    Returns a PIL Image.
    """
    # Attempt to get the filename (default to empty string if not available)
    filename = getattr(file_obj, 'name', '').lower()
    
    # Ensure the file pointer is at the start
    file_obj.seek(0)
    
    # Read the header bytes to help detect HEIC/HEIF if filename is absent or ambiguous
    header = file_obj.read(32)
    file_obj.seek(0)
    
    # Determine if the file is HEIC/HEIF either by filename or header signature.
    is_heic = False
    if filename.endswith(('.heic', '.heif')):
        is_heic = True
    else:
        # Check if header contains typical HEIC signatures.
        # HEIC files usually contain "ftypheic" or "ftyphevc" in their header.
        if b'ftypheic' in header or b'ftyphevc' in header:
            is_heic = True

    if is_heic:
        try:
            # Read the entire file as bytes.
            heif_bytes = file_obj.read()
            file_obj.seek(0)
            heif_file = pyheif.read(heif_bytes)
        except Exception as e:
            raise ValueError(f"Failed to read HEIC file: {e}")
        
        try:
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
        except Exception as e:
            raise ValueError(f"Error converting HEIC data to image: {e}")
        
        return image.convert("RGB")
    else:
        try:
            return Image.open(file_obj)
        except Exception as e:
            raise ValueError(f"Failed to open image: {e}")
