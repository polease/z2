"""
Storage management module for JSON metadata and files
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional
from .utils.logger import get_app_logger

logger = get_app_logger()


class StorageManager:
    """Manage storage of video metadata and files"""

    def __init__(self, storage_path: str = "./storage"):
        """
        Initialize storage manager

        Args:
            storage_path: Base storage path
        """
        self.storage_path = storage_path
        self.data_path = os.path.join(storage_path, "data")

        # Ensure directories exist
        os.makedirs(self.data_path, exist_ok=True)

    def save_metadata(
        self,
        video_id: str,
        year_month: str,
        metadata: Dict
    ) -> str:
        """
        Save video metadata to JSON file

        Args:
            video_id: Video ID
            year_month: Year-month for organization (e.g., "2024-01")
            metadata: Complete metadata dictionary

        Returns:
            Path to saved JSON file
        """
        logger.info(f"Saving metadata for video: {video_id}")

        # Create directory for this month
        data_dir = os.path.join(self.data_path, year_month)
        os.makedirs(data_dir, exist_ok=True)

        # JSON file path
        json_path = os.path.join(data_dir, f"{video_id}.json")

        # Save to file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"Metadata saved to: {json_path}")
        return json_path

    def load_metadata(self, video_id: str, year_month: str) -> Optional[Dict]:
        """
        Load video metadata from JSON file

        Args:
            video_id: Video ID
            year_month: Year-month (e.g., "2024-01")

        Returns:
            Metadata dictionary, or None if not found
        """
        json_path = os.path.join(self.data_path, year_month, f"{video_id}.json")

        if not os.path.exists(json_path):
            logger.warning(f"Metadata file not found: {json_path}")
            return None

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            logger.info(f"Loaded metadata from: {json_path}")
            return metadata

        except Exception as e:
            logger.error(f"Failed to load metadata: {str(e)}")
            return None

    def build_metadata(
        self,
        video_metadata: Dict,
        english_transcript: Dict,
        chinese_transcript: Dict,
        video_processing: Dict,
        analysis: Dict
    ) -> Dict:
        """
        Build complete metadata structure

        Args:
            video_metadata: Video metadata from downloader
            english_transcript: English transcript data
            chinese_transcript: Chinese transcript data
            video_processing: Video processing results
            analysis: Content analysis results

        Returns:
            Complete metadata dictionary
        """
        video_id = video_metadata['video_id']
        upload_date = video_metadata.get('upload_date', datetime.now().strftime('%Y%m%d'))
        year_month = f"{upload_date[:4]}-{upload_date[4:6]}"

        metadata = {
            'video_id': video_id,
            'youtube_url': video_metadata['youtube_url'],
            'processed_date': datetime.now().isoformat(),
            'metadata': {
                'title': video_metadata.get('title', 'Unknown'),
                'channel': video_metadata.get('channel', 'Unknown'),
                'channel_id': video_metadata.get('channel_id', ''),
                'upload_date': upload_date,
                'duration': video_metadata.get('duration', 0),
                'description': video_metadata.get('description', ''),
                'view_count': video_metadata.get('view_count', 0),
                'like_count': video_metadata.get('like_count', 0),
                'thumbnail_url': video_metadata.get('thumbnail_url', ''),
            },
            'files': {
                'original_video': video_metadata.get('video_path', ''),
                'subtitled_video': video_processing.get('subtitled_video_path', ''),
                'english_srt': english_transcript.get('srt_file_path', ''),
                'chinese_srt': chinese_transcript.get('srt_file_path', ''),
            },
            'transcripts': {
                'english': {
                    'source': english_transcript.get('source', 'unknown'),
                    'segment_count': english_transcript.get('segment_count', 0),
                    'full_text': english_transcript.get('full_text', ''),
                },
                'chinese': {
                    'srt_format': True,
                    'segment_count': chinese_transcript.get('segment_count', 0),
                    'full_text': chinese_transcript.get('full_text', ''),
                }
            },
            'processing': {
                'subtitle_burn': {
                    'status': video_processing.get('status', 'unknown'),
                    'output_size_mb': video_processing.get('output_size_mb', 0),
                }
            },
            'analysis': {
                'summary': analysis.get('summary', ''),
                'key_insights': analysis.get('key_insights', []),
                'highlights': analysis.get('highlights', []),
                'topics': analysis.get('topics', []),
            },
            'publishing': {
                'wechat': {
                    'status': 'pending',
                    'published_date': None,
                    'post_id': None,
                    'url': None,
                },
                'bilibili': {
                    'status': 'pending',
                    'published_date': None,
                    'video_id': None,
                    'url': None,
                }
            }
        }

        return metadata

    def update_publishing_status(
        self,
        video_id: str,
        year_month: str,
        platform: str,
        status: str,
        post_id: Optional[str] = None,
        url: Optional[str] = None
    ) -> bool:
        """
        Update publishing status in metadata

        Args:
            video_id: Video ID
            year_month: Year-month
            platform: Platform name (wechat or bilibili)
            status: Publishing status (published, failed, pending)
            post_id: Post/video ID on platform
            url: URL of published content

        Returns:
            True if successful, False otherwise
        """
        metadata = self.load_metadata(video_id, year_month)

        if metadata is None:
            logger.error(f"Cannot update publishing status: metadata not found")
            return False

        # Update publishing info
        if platform in metadata['publishing']:
            metadata['publishing'][platform]['status'] = status

            if status == 'published':
                metadata['publishing'][platform]['published_date'] = datetime.now().isoformat()
                metadata['publishing'][platform]['post_id'] = post_id
                metadata['publishing'][platform]['url'] = url

        # Save updated metadata
        self.save_metadata(video_id, year_month, metadata)

        logger.info(f"Updated {platform} publishing status to: {status}")
        return True

    def get_year_month_from_video_id(self, video_id: str) -> str:
        """
        Extract year-month from video ID (assuming first 8 chars are date)

        Args:
            video_id: Video ID

        Returns:
            Year-month string (e.g., "2024-01")
        """
        if len(video_id) >= 8:
            upload_date = video_id[:8]
            return f"{upload_date[:4]}-{upload_date[4:6]}"
        else:
            # Fallback to current date
            return datetime.now().strftime("%Y-%m")
