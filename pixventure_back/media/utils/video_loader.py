# media/utils/video_loader.py
import cv2

def get_video_metadata(video_path):
    """
    Opens the video file at video_path using OpenCV and returns its width, height, and duration.
    
    :param video_path: Path to the video file.
    :return: (width, height, duration) where duration is in seconds.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video file.")
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count / fps if fps else 0
    cap.release()
    return width, height, duration
