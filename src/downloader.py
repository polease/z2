"""
Video download module using yt-dlp
"""

import os
import yt_dlp
from typing import Dict, Optional
from datetime import datetime
from .utils.logger import get_app_logger

logger = get_app_logger()


class VideoDownloader:
    """YouTube video downloader using yt-dlp"""

    def __init__(self, storage_path: str = "./storage"):
        """
        Initialize video downloader

        Args:
            storage_path: Base storage path for videos
        """
        self.storage_path = storage_path
        self.video_path = os.path.join(storage_path, "videos")

        # Ensure storage directory exists
        os.makedirs(self.video_path, exist_ok=True)

    def download(self, youtube_url: str) -> Dict:
        """
        Download YouTube video and extract metadata

        Args:
            youtube_url: YouTube video URL

        Returns:
            Dictionary with video metadata and file paths

        Raises:
            Exception: If download fails
        """
        logger.info(f"Starting download for URL: {youtube_url}")

        try:
            # Extract video info first
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(youtube_url, download=False)

            video_id = info['id']
            upload_date = info.get('upload_date', datetime.now().strftime('%Y%m%d'))

            # Format: YYYY-MM
            year_month = f"{upload_date[:4]}-{upload_date[4:6]}"
            video_dir = os.path.join(self.video_path, year_month)
            os.makedirs(video_dir, exist_ok=True)

            # Output file path
            output_template = os.path.join(video_dir, f"{video_id}.%(ext)s")

            # Download options
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': output_template,
                'writesubtitles': False,  # We'll handle subtitles separately
                'writeautomaticsub': False,
                'quiet': False,
                'no_warnings': False,
            }

            # Download video
            logger.info(f"Downloading video {video_id}...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            # Get the actual downloaded file path
            video_file = os.path.join(video_dir, f"{video_id}.mp4")

            # Check for available subtitles
            has_subtitles = False
            available_subtitle_languages = []

            if 'subtitles' in info and info['subtitles']:
                has_subtitles = True
                available_subtitle_languages.extend(list(info['subtitles'].keys()))

            if 'automatic_captions' in info and info['automatic_captions']:
                has_subtitles = True
                available_subtitle_languages.extend(list(info['automatic_captions'].keys()))

            # Build metadata response
            metadata = {
                'video_id': video_id,
                'title': info.get('title', 'Unknown'),
                'channel': info.get('uploader', 'Unknown'),
                'channel_id': info.get('channel_id', ''),
                'upload_date': upload_date,
                'duration': info.get('duration', 0),
                'description': info.get('description', ''),
                'thumbnail_url': info.get('thumbnail', ''),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'video_path': video_file,
                'has_subtitles': has_subtitles,
                'available_subtitle_languages': list(set(available_subtitle_languages)),
                'youtube_url': youtube_url,
            }

            logger.info(f"Successfully downloaded video {video_id}")
            logger.info(f"Video saved to: {video_file}")
            logger.info(f"Has subtitles: {has_subtitles}, Languages: {available_subtitle_languages}")

            return metadata

        except Exception as e:
            logger.error(f"Failed to download video: {str(e)}")
            raise

    def download_subtitles(self, youtube_url: str, video_id: str, language: str = 'en') -> Optional[str]:
        """
        Download subtitles for a YouTube video

        Args:
            youtube_url: YouTube video URL
            video_id: Video ID
            language: Subtitle language code (default: 'en')

        Returns:
            Path to downloaded subtitle file, or None if not available
        """
        logger.info(f"Attempting to download subtitles for {video_id} in language: {language}")

        try:
            # Get upload date for directory structure
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(youtube_url, download=False)

            upload_date = info.get('upload_date', datetime.now().strftime('%Y%m%d'))
            year_month = f"{upload_date[:4]}-{upload_date[4:6]}"

            subtitle_dir = os.path.join(self.storage_path, "subtitles", year_month)
            os.makedirs(subtitle_dir, exist_ok=True)

            output_template = os.path.join(subtitle_dir, f"{video_id}")

            # Download options for subtitles
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': [language],
                'subtitlesformat': 'srt',
                'outtmpl': output_template,
                'quiet': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])

            # Check if subtitle file was created
            subtitle_file = os.path.join(subtitle_dir, f"{video_id}.{language}.srt")

            if os.path.exists(subtitle_file):
                logger.info(f"Successfully downloaded subtitles to: {subtitle_file}")
                return subtitle_file
            else:
                logger.warning(f"Subtitle file not found after download attempt")
                return None

        except Exception as e:
            logger.warning(f"Failed to download subtitles: {str(e)}")
            return None
