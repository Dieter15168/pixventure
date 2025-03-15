# media/config.py
"""
Default configuration for media item version creation parameters.
These values will be used if no override is found in the main app settings.
"""

DEFAULT_SETTINGS = {
    "watermarked_preview_quality": 85,
    "full_watermarked_version_quality": 90,
    "blurred_thumbnail_quality": 75,
    "blurred_preview_quality": 75,
    # Separate size settings:
    "thumbnail_size": 300,   # Maximum dimension (width/height) for thumbnails
    "preview_size": 800,     # Maximum dimension for previews
    # Blur radius settings:
    "thumbnail_blur_radius": 20,
    "preview_blur_radius": 20,
    "item_blur_probability": 0.1,
    "post_blur_probability": 0.1,
}
