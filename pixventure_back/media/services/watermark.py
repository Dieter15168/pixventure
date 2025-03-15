# media/services/watermark.py
import io
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from media.models import MediaItemVersion

def set_watermark_in_corner(image: Image.Image, text: str, font_size: int, w_offset: int, h_offset: int) -> Image.Image:
    """
    Adds a watermark to the bottom right corner of the image.
    
    :param image: PIL Image to watermark.
    :param text: Watermark text.
    :param font_size: Size of the watermark font.
    :param w_offset: Horizontal offset from the image edge.
    :param h_offset: Vertical offset from the image edge.
    :return: New watermarked PIL Image.
    """
    font = ImageFont.truetype(settings.FONT_LOCATION, font_size)
    watermarked_image = image.copy()
    watermark_layer = Image.new("RGBA", watermarked_image.size)
    waterdraw = ImageDraw.Draw(watermark_layer, "RGBA")
    
    W, H = watermarked_image.size
    bbox = waterdraw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    waterdraw.text((W - w - w_offset, H - h - h_offset), text, (236, 50, 64), font=font)
    watermarked_image.paste(watermark_layer, (0, 0), watermark_layer)
    
    return watermarked_image

def create_watermarked_preview(media_item) -> InMemoryUploadedFile:
    """
    Creates a watermarked preview version from the original media.
    
    :param media_item: MediaItem instance.
    :return: InMemoryUploadedFile containing the watermarked preview image.
    """
    # Assuming the original version (version_type=ORIGINAL) exists.
    original_file = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL).file
    image = Image.open(original_file).convert("RGB")
    
    # Use settings to choose watermark text and style
    watermarked_image = set_watermark_in_corner(
        image, 
        settings.WATERMARK_TEXT_FOR_PREVIEWS, 
        font_size=20, 
        w_offset=5, 
        h_offset=3
    )
    
    temp_io = io.BytesIO()
    watermarked_image.save(temp_io, format='JPEG', quality=85, optimize=True, progressive=True)
    temp_io.seek(0)
    
    return InMemoryUploadedFile(
        temp_io, None, 'watermarked_preview.jpg', 'image/jpeg', temp_io.getbuffer().nbytes, None
    )

def create_full_watermarked_version(media_item) -> InMemoryUploadedFile:
    """
    Creates a full watermarked version suitable for paid users.
    
    :param media_item: MediaItem instance.
    :return: InMemoryUploadedFile containing the full watermarked image.
    """
    original_file = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL).file
    image = Image.open(original_file).convert("RGB")
    
    watermarked_image = set_watermark_in_corner(
        image, 
        settings.WATERMARK_TEXT_FOR_FULLRES, 
        font_size=30, 
        w_offset=10, 
        h_offset=10
    )
    
    temp_io = io.BytesIO()
    watermarked_image.save(temp_io, format='JPEG', quality=90, optimize=True, progressive=True)
    temp_io.seek(0)
    
    return InMemoryUploadedFile(
        temp_io, None, 'full_watermarked.jpg', 'image/jpeg', temp_io.getbuffer().nbytes, None
    )

def create_blurred_thumbnail(file_obj) -> InMemoryUploadedFile:
    """
    Creates a blurred thumbnail version from an existing thumbnail.
    
    :param file_obj: File object for the thumbnail image.
    :return: InMemoryUploadedFile containing the blurred thumbnail.
    """
    image = Image.open(file_obj)
    # Use a blur radius defined in settings or default to 5
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=getattr(settings, 'THUMBNAIL_BLUR_RADIUS', 5)))
    
    temp_io = io.BytesIO()
    blurred_image.save(temp_io, format='JPEG', quality=75, optimize=True, progressive=True)
    temp_io.seek(0)
    
    return InMemoryUploadedFile(
        temp_io, None, 'blurred_thumbnail.jpg', 'image/jpeg', temp_io.getbuffer().nbytes, None
    )

def create_blurred_preview(media_item) -> InMemoryUploadedFile:
    """
    Creates a blurred preview version.
    
    :param media_item: MediaItem instance.
    :return: InMemoryUploadedFile containing the blurred preview.
    """
    original_file = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL).file
    image = Image.open(original_file).convert("RGB")
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=getattr(settings, 'PREVIEW_BLUR_RADIUS', 5)))
    
    # Optionally add watermark after blurring
    blurred_image = set_watermark_in_corner(
        blurred_image, 
        settings.WATERMARK_TEXT_FOR_PREVIEWS, 
        font_size=20, 
        w_offset=5, 
        h_offset=3
    )
    
    temp_io = io.BytesIO()
    blurred_image.save(temp_io, format='JPEG', quality=75, optimize=True, progressive=True)
    temp_io.seek(0)
    
    return InMemoryUploadedFile(
        temp_io, None, 'blurred_preview.jpg', 'image/jpeg', temp_io.getbuffer().nbytes, None
    )
