# media/services/video_metadata.py
import subprocess
import json
import os
import tempfile
import logging

logger = logging.getLogger(__name__)

def extract_video_metadata(file_obj) -> dict:
    """
    Extracts video metadata (width, height, duration) using mediainfo.
    
    If file_obj lacks a .path attribute (e.g. InMemoryUploadedFile), its contents
    are read and written to a temporary file. The size of the temporary file is logged.
    
    If extraction fails, default values are returned.
    
    :param file_obj: A file-like object.
    :return: A dict with keys: "width", "height", "duration" (in seconds).
    """
    remove_temp = False

    # Ensure we start at the beginning
    try:
        file_obj.seek(0)
    except Exception:
        pass

    if hasattr(file_obj, 'path'):
        tmp_path = file_obj.path
    else:
        try:
            content = file_obj.read()
        except Exception as e:
            logger.error("Failed to read file object: %s", e)
            raise
        file_obj.seek(0)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = tmp.name
        remove_temp = True

    # Log the size of the temporary file to ensure it is not empty.
    try:
        temp_size = os.path.getsize(tmp_path)
        logger.debug("Temporary file %s size: %d bytes", tmp_path, temp_size)
    except Exception as e:
        logger.error("Could not get size of temporary file %s: %s", tmp_path, e)
    
    cmd = ["mediainfo", "--Output=JSON", tmp_path]
    logger.debug("Running mediainfo command: %s", " ".join(cmd))
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        logger.debug("mediainfo stdout: %s", result.stdout)
        logger.debug("mediainfo stderr: %s", result.stderr)
        data = json.loads(result.stdout)
        if "media" not in data or "track" not in data["media"]:
            raise Exception("No track data in mediainfo output.")
        video_track = None
        for track in data["media"]["track"]:
            if track.get("@type") == "Video":
                video_track = track
                break
        if not video_track:
            raise Exception("No video track found in mediainfo output.")
        try:
            width = int(video_track.get("Width", 0))
        except Exception:
            width = 0
        try:
            height = int(video_track.get("Height", 0))
        except Exception:
            height = 0
        try:
            # Duration is usually in milliseconds.
            duration = float(video_track.get("Duration", 0)) / 1000.0
        except Exception:
            duration = 0.0
        logger.debug("Extracted metadata: width=%s, height=%s, duration=%s", width, height, duration)
        return {"width": width, "height": height, "duration": duration}
    except Exception as e:
        logger.error("mediainfo extraction failed: %s", e)
        return {"width": 0, "height": 0, "duration": 0.0}
    finally:
        if remove_temp:
            try:
                os.remove(tmp_path)
                logger.debug("Removed temporary file: %s", tmp_path)
            except Exception as e:
                logger.warning("Could not remove temporary file %s: %s", tmp_path, e)
