# media/config.py
"""
Default configuration for media item version creation parameters.
These values will be used if no override is found in the main app settings.
"""

DEFAULT_MEDIA_SETTINGS = {
    "watermarked_preview_quality": 80,
    "full_watermarked_version_quality": 90,
    "blurred_thumbnail_quality": 70,
    "blurred_preview_quality": 70,
    # New separate size settings:
    "thumbnail_size": 300,   # Maximum dimension (width/height) for thumbnails
    "preview_size": 800,     # Maximum dimension for previews
}
