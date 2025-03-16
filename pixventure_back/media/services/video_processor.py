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
    """
    Creates a watermarked full-resolution version of the video using two-pass encoding.
    
    This method overlays a watermark and then re-encodes the video using two passes
    to target a bitrate computed from the original video's size and duration.
    
    Parameters:
      - quality: if provided as a non-negative integer, it is used as the CRF value for the second pass.
                 If quality is negative or invalid, a default CRF of 18 is used.
      - max_video_bitrate: the maximum allowed bitrate in bits per second.
    
    Audio is copied to preserve its quality.
    
    Returns a tuple: (InMemoryUploadedFile, video_duration).
    """
    # Convert parameters to integers
    try:
        quality = int(quality)
    except Exception:
        quality = -1
    if quality < 0:
        quality = 18  # default high-quality CRF value

    try:
        max_video_bitrate = int(max_video_bitrate)
    except Exception:
        max_video_bitrate = 5000000  # default fallback in bps

    # Get original video details.
    original_version = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL)
    input_path = original_version.file.path
    width, height, duration = get_video_metadata(input_path)
    if width % 2 != 0:
        width += 1
    if height % 2 != 0:
        height += 1

    try:
        size_bytes = os.path.getsize(input_path)
    except Exception:
        raise ValueError("Failed to determine file size.")

    # Compute the original video's bitrate in bits per second.
    computed_bitrate = int((size_bytes * 8) / duration) if duration > 0 else 0
    # Cap bitrate at max_video_bitrate.
    target_bitrate = computed_bitrate if computed_bitrate <= max_video_bitrate else max_video_bitrate

    # For two-pass encoding, FFmpeg expects the bitrate in kilobits.
    target_bitrate_k = target_bitrate // 1000

    output_filename = random_alphanumeric_string(30) + '.mp4'
    destination_folder = os.path.join('watermarked_video')
    os.makedirs(destination_folder, exist_ok=True)
    output_path = os.path.join(destination_folder, output_filename)

    watermark_text = getattr(settings, "WATERMARK_TEXT_FOR_PREVIEWS", "Default Watermark")

    # Build the base filter: watermark overlay and scaling.
    # (You could refine the filter if needed.)
    filter_str = f"drawtext=text='{watermark_text}':x=w-tw-10:y=h-th-10:fontsize=17:fontcolor=red,scale={width}:{height}"

    # Define a temporary passlog file prefix.
    passlog = os.path.join(destination_folder, "passlog")

    # --- First pass ---
    # In first pass we don't output audio and we output to null.
    ffmpeg_pass1 = [
        'ffmpeg',
        '-y',                      # Overwrite output files
        '-i', input_path,
        '-vf', filter_str,
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-b:v', f'{target_bitrate_k}k',  # set target bitrate for analysis
        '-pass', '1',
        '-passlogfile', passlog,
        '-an',                     # no audio
        '-f', 'mp4',
        os.devnull
    ]
    subprocess.run(ffmpeg_pass1, check=True)

    # --- Second pass ---
    # In second pass, we encode the video with audio copy and target the computed bitrate.
    ffmpeg_pass2 = [
        'ffmpeg',
        '-y',
        '-i', input_path,
        '-vf', filter_str,
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-b:v', f'{target_bitrate_k}k',
        '-minrate', f'{target_bitrate_k}k',
        '-maxrate', f'{target_bitrate_k}k',
        '-bufsize', f'{target_bitrate_k * 2}k',
        '-pass', '2',
        '-passlogfile', passlog,
        '-c:a', 'copy',
        '-f', 'mp4',
        output_path
    ]
    subprocess.run(ffmpeg_pass2, check=True)

    # Clean up temporary log files (they usually have names like passlog-0.log, etc.)
    for filename in os.listdir(destination_folder):
        if filename.startswith("passlog"):
            try:
                os.remove(os.path.join(destination_folder, filename))
            except Exception:
                pass

    # Read the output file into memory.
    with open(output_path, 'rb') as f:
        file_data = f.read()
    from io import BytesIO
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
    
    For the preview, we use a similar two-pass approach (if desired), but since the preview is short,
    you might opt for a single pass. Here we'll use a single-pass CRF encode to keep things simple.
    """
    from media.models import MediaItemVersion
    watermarked_version = media_item.versions.get(version_type=MediaItemVersion.WATERMARKED)
    input_path = watermarked_version.file.path
    output_filename = random_alphanumeric_string(30) + '.mp4'
    destination_folder = os.path.join('short_video_preview')
    os.makedirs(destination_folder, exist_ok=True)
    output_path = os.path.join(destination_folder, output_filename)

    try:
        quality = int(quality)
    except Exception:
        quality = -1
    if quality < 0:
        quality = 18

    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-i', input_path,
        '-t', str(preview_duration),
        '-c:v', 'libx264',
        '-preset', 'slow',
        '-crf', str(quality),
        '-c:a', 'copy',
        '-f', 'mp4',
        output_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)

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
    The frame is converted to WEBP.
    """
    original_version = media_item.versions.get(version_type=MediaItemVersion.ORIGINAL)
    input_path = original_version.file.path
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
