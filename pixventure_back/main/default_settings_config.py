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
    # Probability of newly created item to get is_blurred=True
    "item_blur_probability": 0.1,
    # Probability of newly created post to get is_blurred=True
    "post_blur_probability": 0.1,
    "full_watermark_transparency": 50,
    # Maximum bitrate for full watermarked video; original videos wight higher bitrate will have their bitrate reduced
    "max_video_bitrate": 5000000,
    # Duration of the short preview video in seconds
    "preview_video_duration": 5,
    # In current implementation - CRF value between 0 and 51, where 18 is considered good quality; -1 for using defaults (currently 18)
    "full_watermarked_version_quality": -1, 
    # Same
    "preview_video_quality": -1,
}
