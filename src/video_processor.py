"""
Video processing and subtitle burning module using FFmpeg
"""

import os
import ffmpeg
from typing import Dict
from .utils.logger import get_app_logger

logger = get_app_logger()


class VideoProcessor:
    """Process videos and burn subtitles using FFmpeg"""

    def __init__(
        self,
        storage_path: str = "./storage",
        font_name: str = "SimHei",
        font_size: int = 24,
        primary_color: str = "&H00FFFFFF",
        outline_color: str = "&H00000000"
    ):
        """
        Initialize video processor

        Args:
            storage_path: Base storage path
            font_name: Font name for subtitles
            font_size: Font size for subtitles
            primary_color: Primary text color (ASS format)
            outline_color: Outline color (ASS format)
        """
        self.storage_path = storage_path
        self.video_path = os.path.join(storage_path, "videos")
        self.font_name = font_name
        self.font_size = font_size
        self.primary_color = primary_color
        self.outline_color = outline_color

        # Ensure video directory exists
        os.makedirs(self.video_path, exist_ok=True)

    def burn_subtitles(
        self,
        video_path: str,
        srt_path: str,
        video_id: str,
        year_month: str
    ) -> Dict:
        """
        Burn Chinese subtitles into video

        Args:
            video_path: Path to original video file
            srt_path: Path to Chinese SRT file
            video_id: Video ID
            year_month: Year-month for directory organization

        Returns:
            Dictionary with processing results
        """
        logger.info(f"Burning subtitles for video: {video_id}")
        logger.info(f"Video: {video_path}")
        logger.info(f"Subtitles: {srt_path}")

        try:
            # Output video path
            video_dir = os.path.join(self.video_path, year_month)
            os.makedirs(video_dir, exist_ok=True)
            output_path = os.path.join(video_dir, f"{video_id}_zh_subbed.mp4")

            # Build subtitle filter with styling
            subtitle_style = (
                f"FontName={self.font_name},"
                f"FontSize={self.font_size},"
                f"PrimaryColour={self.primary_color},"
                f"OutlineColour={self.outline_color},"
                "BorderStyle=1,"
                "Outline=2,"
                "Shadow=1"
            )

            # Normalize path for FFmpeg (handle spaces and special characters)
            srt_path_escaped = srt_path.replace('\\', '/').replace(':', '\\:')

            logger.info("Starting FFmpeg subtitle burning...")

            # Use FFmpeg to burn subtitles
            input_stream = ffmpeg.input(video_path)

            # Get video and audio streams separately
            video = input_stream.video
            audio = input_stream.audio

            # Apply subtitle filter to video stream only
            video_with_subs = ffmpeg.filter(
                video,
                'subtitles',
                srt_path_escaped,
                force_style=subtitle_style
            )

            # Output with subtitled video and copied audio
            # Use Baseline profile for maximum compatibility with all platforms
            stream = ffmpeg.output(
                video_with_subs,
                audio,
                output_path,
                vcodec='libx264',
                acodec='aac',  # Re-encode audio to AAC for compatibility
                **{
                    'profile:v': 'baseline',  # Baseline profile for maximum compatibility
                    'level': '3.1',           # Level 3.1 supports most devices
                    'pix_fmt': 'yuv420p',     # Standard pixel format
                    'movflags': '+faststart', # Enable fast start for web playback
                    'preset': 'medium',       # Balance between speed and quality
                    'crf': '23'               # Constant quality (lower = better quality)
                }
            )

            # Run FFmpeg
            ffmpeg.run(stream, overwrite_output=True, quiet=False)

            # Get output file size
            output_size_mb = os.path.getsize(output_path) / (1024 * 1024)

            logger.info(f"Successfully burned subtitles into video")
            logger.info(f"Output file: {output_path}")
            logger.info(f"Output size: {output_size_mb:.2f} MB")

            result = {
                'original_video_path': video_path,
                'subtitled_video_path': output_path,
                'srt_file_used': srt_path,
                'output_size_mb': round(output_size_mb, 2),
                'status': 'completed'
            }

            return result

        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"FFmpeg error while burning subtitles: {error_message}")
            raise

        except Exception as e:
            logger.error(f"Failed to burn subtitles: {str(e)}")
            raise

    def get_video_info(self, video_path: str) -> Dict:
        """
        Get video file information

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video information
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_info = next(
                (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
                None
            )

            if video_info:
                return {
                    'width': int(video_info.get('width', 0)),
                    'height': int(video_info.get('height', 0)),
                    'codec': video_info.get('codec_name', 'unknown'),
                    'duration': float(probe['format'].get('duration', 0)),
                    'size_mb': float(probe['format'].get('size', 0)) / (1024 * 1024)
                }

            return {}

        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            return {}
