# media/services/video_processor.py
import os
import subprocess
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from media.utils.video_loader import get_video_metadata
from main.utils import random_alphanumeric_string
from media.models import MediaItemVersion

def create_watermarked_video(media_item, quality, max_video_bitrate):
    from media.models import MediaItemVersion
    original_version = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL)
    input_path = original_version.file.path
    width, height, duration = get_video_metadata(input_path)
    
    if width % 2 != 0: width += 1
    if height % 2 != 0: height += 1
    
    try:
        size_bytes = os.path.getsize(input_path)
    except Exception:
        raise ValueError("Failed to determine file size.")
    
    bitrate = int((size_bytes * 8) / duration) if duration > 0 else 0
    if bitrate > max_video_bitrate:
        bitrate = max_video_bitrate
    
    output_filename = random_alphanumeric_string(30) + '.mp4'
    destination_folder = os.path.join('watermarked_video')
    os.makedirs(destination_folder, exist_ok=True)
    output_path = os.path.join(destination_folder, output_filename)
    
    watermark_text = getattr(settings, "WATERMARK_TEXT_FOR_PREVIEWS", "Default Watermark")
    
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', input_path,
        '-vf', f"drawtext=text='{watermark_text}':x=w-tw-10:y=h-th-10:fontsize=17:fontcolor=red",
        '-b:v', str(bitrate),
        '-s', f'{width}x{height}',
        '-f', 'mp4',
        output_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    
    # Read the output file into memory
    with open(output_path, 'rb') as f:
        file_data = f.read()
    temp_io = BytesIO(file_data)
    video_file = InMemoryUploadedFile(
        temp_io,
        None,
        os.path.basename(output_path),
        'video/mp4',
        len(file_data),
        None
    )
    
    os.remove(output_path)
    return video_file, duration

def create_video_preview(media_item, quality, preview_duration):
    """
    Creates a short preview version of the watermarked video.
    """
    from media.models import MediaItemVersion  # Ensure correct constant usage
    
    # Retrieve the watermarked version using the correct constant.
    watermarked_version = media_item.versions.get(version_type=MediaItemVersion.WATERMARKED)
    input_path = watermarked_version.file.path
    output_filename = random_alphanumeric_string(30) + '.mp4'
    destination_folder = os.path.join('short_video_preview')
    os.makedirs(destination_folder, exist_ok=True)
    output_path = os.path.join(destination_folder, output_filename)
    
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', input_path,
        '-t', str(preview_duration),
        '-f', 'mp4',
        output_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    
    # Read the generated file into memory.
    with open(output_path, 'rb') as f:
        file_bytes = f.read()
    from io import BytesIO
    temp_io = BytesIO(file_bytes)
    
    preview_file = InMemoryUploadedFile(
        temp_io,
        None,
        os.path.basename(output_path),
        'video/mp4',
        len(file_bytes),
        None
    )
    
    os.remove(output_path)
    return preview_file


def create_video_thumbnail(media_item):
    """
    Extracts a frame from the middle of the original video and creates a thumbnail image.
    The extracted frame is converted to WEBP format.
    """
    # Correctly reference the ORIGINAL constant.
    original_version = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL)
    input_path = original_version.file.path
    
    # Get video metadata to find middle time.
    _, _, duration = get_video_metadata(input_path)
    middle_time = duration / 2 if duration > 0 else 0
    
    output_filename = random_alphanumeric_string(30) + '.png'
    destination_folder = os.path.join('video_thumbnail')
    os.makedirs(destination_folder, exist_ok=True)
    output_path = os.path.join(destination_folder, output_filename)
    
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', input_path,
        '-ss', str(middle_time),
        '-frames:v', '1',
        output_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    
    from PIL import Image
    with Image.open(output_path) as img:
        img = img.convert("RGB")
        temp_io = BytesIO()
        img.save(temp_io, format='WEBP', quality=85, optimize=True)
        temp_io.seek(0)
    
    thumbnail_file = InMemoryUploadedFile(
        temp_io,
        None,
        os.path.basename(output_path).replace('.png', '.webp'),
        'image/webp',
        temp_io.getbuffer().nbytes,
        None
    )
    os.remove(output_path)
    return thumbnail_file
