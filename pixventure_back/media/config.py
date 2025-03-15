# media/config.py
"""
Default configuration for media item version creation parameters.
These values will be used if no override is found in the main app settings.
"""

DEFAULT_MEDIA_SETTINGS = {
    "watermarked_preview_quality": 85,
    "full_watermarked_version_quality": 90,
    "blurred_thumbnail_quality": 75,
    "blurred_preview_quality": 75,
    # Maximum size in pixels (both width and height)
    "max_version_size": 1024,
}
