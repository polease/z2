"""
Subtitle extraction and transcription module
"""

import os
import whisper
from typing import Dict, List, Optional
from .utils.logger import get_app_logger
from .utils.srt_utils import create_srt_file, read_srt_file

logger = get_app_logger()


class SubtitleProcessor:
    """Process subtitles from YouTube or transcribe using Whisper"""

    def __init__(
        self,
        storage_path: str = "./storage",
        whisper_model: str = "medium",
        device: str = "cpu"
    ):
        """
        Initialize subtitle processor

        Args:
            storage_path: Base storage path
            whisper_model: Whisper model name (tiny, base, small, medium, large)
            device: Device to run Whisper on (cpu or cuda)
        """
        self.storage_path = storage_path
        self.subtitle_path = os.path.join(storage_path, "subtitles")
        self.whisper_model_name = whisper_model
        self.device = device
        self.whisper_model = None

        # Ensure subtitle directory exists
        os.makedirs(self.subtitle_path, exist_ok=True)

    def _load_whisper_model(self):
        """Lazy load Whisper model"""
        if self.whisper_model is None:
            logger.info(f"Loading Whisper model: {self.whisper_model_name}")
            self.whisper_model = whisper.load_model(
                self.whisper_model_name,
                device=self.device
            )
            logger.info("Whisper model loaded successfully")

    def process(
        self,
        video_metadata: Dict,
        subtitle_file: Optional[str] = None
    ) -> Dict:
        """
        Process subtitles: use existing YouTube subtitles or transcribe with Whisper

        Args:
            video_metadata: Video metadata from downloader
            subtitle_file: Path to existing subtitle file (if available)

        Returns:
            Dictionary with transcript data and SRT file path
        """
        video_id = video_metadata['video_id']
        video_path = video_metadata['video_path']

        logger.info(f"Processing subtitles for video: {video_id}")

        # If subtitle file provided, use it
        if subtitle_file and os.path.exists(subtitle_file):
            logger.info(f"Using existing subtitle file: {subtitle_file}")
            return self._process_existing_subtitles(subtitle_file, video_id, source="youtube")

        # Otherwise, transcribe with Whisper
        logger.info("No subtitles found, transcribing with Whisper...")
        return self._transcribe_with_whisper(video_path, video_id)

    def _process_existing_subtitles(
        self,
        subtitle_file: str,
        video_id: str,
        source: str = "youtube"
    ) -> Dict:
        """
        Process existing subtitle file

        Args:
            subtitle_file: Path to subtitle file
            video_id: Video ID
            source: Source of subtitles (youtube or whisper)

        Returns:
            Transcript data dictionary
        """
        try:
            # Read SRT file
            segments = read_srt_file(subtitle_file)

            # Combine full text
            full_text = "\n".join([seg['text'] for seg in segments])

            result = {
                'source': source,
                'language': 'en',
                'srt_file_path': subtitle_file,
                'segments': segments,
                'full_text': full_text,
                'segment_count': len(segments)
            }

            logger.info(f"Processed {len(segments)} subtitle segments from {source}")
            return result

        except Exception as e:
            logger.error(f"Failed to process existing subtitles: {str(e)}")
            raise

    def _transcribe_with_whisper(self, video_path: str, video_id: str) -> Dict:
        """
        Transcribe video using Whisper

        Args:
            video_path: Path to video file
            video_id: Video ID

        Returns:
            Transcript data dictionary
        """
        try:
            # Load Whisper model
            self._load_whisper_model()

            logger.info(f"Transcribing video: {video_path}")

            # Transcribe
            result = self.whisper_model.transcribe(
                video_path,
                language='en',
                verbose=False
            )

            # Convert Whisper segments to our format
            segments = []
            for i, seg in enumerate(result['segments'], start=1):
                segments.append({
                    'index': i,
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip()
                })

            # Create SRT file
            upload_date = video_id[:8] if len(video_id) >= 8 else "unknown"
            year_month = f"{upload_date[:4]}-{upload_date[4:6]}" if upload_date != "unknown" else "unknown"

            subtitle_dir = os.path.join(self.subtitle_path, year_month)
            os.makedirs(subtitle_dir, exist_ok=True)

            srt_file_path = os.path.join(subtitle_dir, f"{video_id}_en.srt")
            create_srt_file(segments, srt_file_path)

            logger.info(f"Created SRT file: {srt_file_path}")

            # Read back the SRT file to get properly formatted segments
            formatted_segments = read_srt_file(srt_file_path)

            # Combine full text
            full_text = result['text']

            transcript_data = {
                'source': 'whisper',
                'language': 'en',
                'srt_file_path': srt_file_path,
                'segments': formatted_segments,
                'full_text': full_text,
                'segment_count': len(formatted_segments)
            }

            logger.info(f"Successfully transcribed {len(formatted_segments)} segments")
            return transcript_data

        except Exception as e:
            logger.error(f"Failed to transcribe with Whisper: {str(e)}")
            raise

    def extract_audio(self, video_path: str, audio_path: str) -> str:
        """
        Extract audio from video file (if needed for optimization)

        Args:
            video_path: Path to video file
            audio_path: Path to save audio file

        Returns:
            Path to audio file
        """
        import ffmpeg

        try:
            logger.info(f"Extracting audio from {video_path}")

            ffmpeg.input(video_path).output(
                audio_path,
                acodec='pcm_s16le',
                ac=1,
                ar='16k'
            ).overwrite_output().run(quiet=True)

            logger.info(f"Audio extracted to: {audio_path}")
            return audio_path

        except Exception as e:
            logger.error(f"Failed to extract audio: {str(e)}")
            raise
