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

def biased_coordinate(total, margin_fraction=0.2):
    """
    Returns a random integer in the range [0, total] that is biased toward the edges.
    
    :param total: The maximum value of the coordinate.
    :param margin_fraction: Fraction of total to use as the margin for bias.
    :return: An integer coordinate, biased to be near 0 or near total.
    """
    margin = int(total * margin_fraction)
    if total <= margin:
        return random.randint(0, total)
    # With 50% chance, pick from the lower margin; otherwise, from the upper margin.
    if random.random() < 0.5:
        return random.randint(0, margin)
    else:
        return random.randint(total - margin, total)

def set_random_transparent_watermark(image: Image.Image, text: str, min_image_fraction: int, max_image_fraction: int, number_of_lines: int, transparency: int = 80) -> Image.Image:
    """
    Adds one or more semi-transparent watermarks to an image, preferring to place them near the edges.
    
    :param image: PIL Image.
    :param text: Watermark text.
    :param min_image_fraction: Minimum percentage (of image width) used to determine font size.
    :param max_image_fraction: Maximum percentage (of image width) used to determine font size.
    :param number_of_lines: Number of watermark lines to add.
    :param transparency: Alpha value for watermark text (0=transparent, 255=opaque). Default is 85.
    :return: New PIL Image with watermarks applied.
    """
    import imageio
    import numpy as np

    def is_light(img_array, threshold):
        return np.mean(img_array) > threshold

    base_image = image.convert("RGBA")
    
    for _ in range(number_of_lines):
        W, H = base_image.size
        image_fraction = random.uniform(min_image_fraction, max_image_fraction) / 100.0

        font_size = 5
        font = ImageFont.truetype(settings.FONT_LOCATION, font_size)
        while font.getbbox(text)[2] < image_fraction * W:
            font_size += 1
            font = ImageFont.truetype(settings.FONT_LOCATION, font_size)
        font_size = max(1, font_size - 1)
        font = ImageFont.truetype(settings.FONT_LOCATION, font_size)

        watermark_layer = Image.new("RGBA", base_image.size)
        waterdraw = ImageDraw.Draw(watermark_layer, "RGBA")

        bbox = waterdraw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        max_x = max(W - text_width - 3, 0)
        max_y = max(H - text_height - 3, 0)
        x = biased_coordinate(max_x, margin_fraction=0.2)
        y = biased_coordinate(max_y, margin_fraction=0.2)

        image_area = base_image.crop((x, y, x + text_width, y + text_height))
        temp_io = io.BytesIO()
        image_area.convert("RGB").save(temp_io, format="JPEG", quality=95, optimize=True, progressive=True)
        temp_io.seek(0)
        image_area_gray = imageio.imread(temp_io, mode='F')
        light_threshold = 80

        if np.mean(image_area_gray) > light_threshold:
            text_color = (0, 0, 0, transparency)
        else:
            text_color = (255, 255, 255, transparency)

        waterdraw.text((x, y), text, fill=text_color, font=font)
        base_image = Image.alpha_composite(base_image, watermark_layer)
    
    return base_image.convert("RGB")

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

def create_full_watermarked_version(media_item, quality=90, watermark_transparency=80) -> InMemoryUploadedFile:
    """
    Creates a full watermarked version (for paid users) with an inconspicuous, random watermark.
    The watermark is applied using a random position and a font size determined by image resolution.
    
    :param media_item: MediaItem instance.
    :param quality: Quality for the output image; defaults to settings.WATERMARKED_VERSION_QUALITY.
    :return: InMemoryUploadedFile containing the full watermarked image in WEBP format.
    """

    # Get the original file (assume version_type ORIGINAL exists)
    original_file = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL).file
    image = Image.open(original_file).convert("RGB")
    
    # Determine image resolution and choose watermark parameters accordingly.
    width, height = image.size
    image_resolution = width * height
    if image_resolution < 250000:
        # For smaller images, use larger watermark proportions.
        min_fraction, max_fraction = 17, 18
    else:
        min_fraction, max_fraction = 12, 13

    # Use the configured watermark text for full resolution from settings.
    watermark_text = getattr(settings, "WATERMARK_TEXT_FOR_FULLRES", "Default Watermark")
    
    # Apply a random, transparent watermark.
    watermarked_image = set_random_transparent_watermark(image, watermark_text, min_fraction, max_fraction, number_of_lines=1, transparency=watermark_transparency)
    
    # Save the watermarked image to an in-memory file as WEBP.
    temp_io = io.BytesIO()
    watermarked_image.save(temp_io, format="WEBP", quality=quality, optimize=True)
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
