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
    font = ImageFont.truetype(settings.FONT_LOCATION, int(font_size))
    watermarked_image = image.copy()
    watermark_layer = Image.new("RGBA", watermarked_image.size)
    waterdraw = ImageDraw.Draw(watermark_layer, "RGBA")
    
    W, H = watermarked_image.size
    bbox = waterdraw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    waterdraw.text((W - w - int(w_offset), H - h - int(h_offset)), text, (236, 50, 64), font=font)
    watermarked_image.paste(watermark_layer, (0, 0), watermark_layer)
    
    return watermarked_image

def create_watermarked_preview(media_item, quality=85, preview_size=800) -> InMemoryUploadedFile:
    """
    Creates a watermarked preview version from the original media.
    
    :param media_item: MediaItem instance.
    :param quality: Quality for the preview image.
    :param preview_size: Maximum dimension (width/height) for the preview.
    :return: InMemoryUploadedFile containing the watermarked preview image in WEBP format.
    """
    quality = int(quality)
    preview_size = int(preview_size)
    
    original_file = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL).file
    image = Image.open(original_file).convert("RGB")
    
    # Resize image to preview size
    image.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)
    
    watermarked_image = set_watermark_in_corner(
        image, 
        text=settings.WATERMARK_TEXT_FOR_PREVIEWS, 
        font_size=20, 
        w_offset=5, 
        h_offset=3
    )
    
    temp_io = io.BytesIO()
    watermarked_image.save(temp_io, format='WEBP', quality=quality, optimize=True)
    temp_io.seek(0)
    
    return InMemoryUploadedFile(
        temp_io, None, 'watermarked_preview.webp', 'image/webp', temp_io.getbuffer().nbytes, None
    )

def create_full_watermarked_version(media_item, quality=90) -> InMemoryUploadedFile:
    """
    Creates a full watermarked version suitable for paid users.
    
    :param media_item: MediaItem instance.
    :param quality: Quality for the full watermarked image.
    :return: InMemoryUploadedFile containing the full watermarked image in WEBP format.
    """
    quality = int(quality)
    
    original_file = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL).file
    image = Image.open(original_file).convert("RGB")
    
    watermarked_image = set_watermark_in_corner(
        image, 
        text=settings.WATERMARK_TEXT_FOR_FULLRES, 
        font_size=30, 
        w_offset=10, 
        h_offset=10
    )
    
    temp_io = io.BytesIO()
    watermarked_image.save(temp_io, format='WEBP', quality=quality, optimize=True)
    temp_io.seek(0)
    
    return InMemoryUploadedFile(
        temp_io, None, 'full_watermarked.webp', 'image/webp', temp_io.getbuffer().nbytes, None
    )

def create_blurred_thumbnail(file_obj, quality=75, thumbnail_size=300, blur_radius=None) -> InMemoryUploadedFile:
    """
    Creates a blurred thumbnail version from an existing thumbnail.
    
    :param file_obj: File object for the thumbnail image.
    :param quality: Quality for the blurred thumbnail.
    :param thumbnail_size: Maximum dimension (width/height) for the thumbnail.
    :param blur_radius: Blur radius for Gaussian blur; if not provided, defaults to 5.
    :return: InMemoryUploadedFile containing the blurred thumbnail in WEBP format.
    """
    quality = int(quality)
    thumbnail_size = int(thumbnail_size)
    
    image = Image.open(file_obj)
    if blur_radius is None:
        blur_radius = 5
    else:
        blur_radius = float(blur_radius)
    
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    blurred_image.thumbnail((thumbnail_size, thumbnail_size), Image.Resampling.LANCZOS)
    
    temp_io = io.BytesIO()
    blurred_image.save(temp_io, format='WEBP', quality=quality, optimize=True)
    temp_io.seek(0)
    
    return InMemoryUploadedFile(
        temp_io, None, 'blurred_thumbnail.webp', 'image/webp', temp_io.getbuffer().nbytes, None
    )

def create_blurred_preview(media_item, quality=75, preview_size=800, blur_radius=None) -> InMemoryUploadedFile:
    """
    Creates a blurred preview version.
    
    :param media_item: MediaItem instance.
    :param quality: Quality for the blurred preview.
    :param preview_size: Maximum dimension (width/height) for the preview.
    :param blur_radius: Blur radius for Gaussian blur; if not provided, defaults to 5.
    :return: InMemoryUploadedFile containing the blurred preview in WEBP format.
    """
    quality = int(quality)
    preview_size = int(preview_size)
    
    original_file = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL).file
    image = Image.open(original_file).convert("RGB")
    
    if blur_radius is None:
        blur_radius = 5
    else:
        blur_radius = float(blur_radius)
    
    image.thumbnail((preview_size, preview_size), Image.Resampling.LANCZOS)
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    
    blurred_image = set_watermark_in_corner(
        blurred_image, 
        text=settings.WATERMARK_TEXT_FOR_PREVIEWS, 
        font_size=20, 
        w_offset=5, 
        h_offset=3
    )
    
    temp_io = io.BytesIO()
    blurred_image.save(temp_io, format='WEBP', quality=quality, optimize=True)
    temp_io.seek(0)
    
    return InMemoryUploadedFile(
        temp_io, None, 'blurred_preview.webp', 'image/webp', temp_io.getbuffer().nbytes, None
    )
