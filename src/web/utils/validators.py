"""
Validation utilities
"""
import re
from typing import Optional


def extract_youtube_video_id(url: str) -> Optional[str]:
    """
    Extract video ID from YouTube URL

    Supports formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def is_valid_youtube_url(url: str) -> bool:
    """Check if URL is a valid YouTube URL"""
    return extract_youtube_video_id(url) is not None
