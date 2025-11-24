"""
Main pipeline orchestrator for Z AI Knowledge Distillery Platform
"""

import sys
import argparse
from datetime import datetime
from typing import Optional

from .downloader import VideoDownloader
from .transcriber import SubtitleProcessor
from .translator import Translator
from .video_processor import VideoProcessor
from .analyzer import ContentAnalyzer
from .storage import StorageManager
from .publisher import Publisher
from .utils.config import get_config
from .utils.logger import setup_logger, get_video_logger

logger = setup_logger("z2.main", log_file="logs/z2.log")


class Pipeline:
    """Main processing pipeline"""

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize pipeline with configuration

        Args:
            config_path: Path to configuration file
        """
        logger.info("Initializing Z Pipeline...")

        # Load configuration
        self.config = get_config(config_path)

        # Initialize modules
        storage_path = self.config.storage_path

        self.downloader = VideoDownloader(storage_path=storage_path)

        self.transcriber = SubtitleProcessor(
            storage_path=storage_path,
            whisper_model=self.config.whisper_model,
            device=self.config.whisper_device
        )

        self.translator = Translator(
            api_key=self.config.openai_api_key,
            storage_path=storage_path,
            model=self.config.get('openai.model', 'gpt-4o-mini'),
            max_chars_per_line=self.config.get('translation.max_subtitle_chars', 42)
        )

        self.video_processor = VideoProcessor(
            storage_path=storage_path,
            font_name=self.config.get('subtitle_style.font_name', 'SimHei'),
            font_size=self.config.get('subtitle_style.font_size', 24),
            primary_color=self.config.get('subtitle_style.primary_color', '&H00FFFFFF'),
            outline_color=self.config.get('subtitle_style.outline_color', '&H00000000')
        )

        self.analyzer = ContentAnalyzer(
            api_key=self.config.openai_api_key,
            model=self.config.get('openai.model', 'gpt-4o-mini')
        )

        self.storage = StorageManager(storage_path=storage_path)

        self.publisher = Publisher(
            storage_path=storage_path,
            schedule_hours_ahead=0  # Immediate publish by default
        )

        logger.info("Pipeline initialized successfully")

    def process_video(self, youtube_url: str) -> Optional[str]:
        """
        Process a YouTube video through the complete pipeline

        Args:
            youtube_url: YouTube video URL

        Returns:
            Path to saved metadata JSON file, or None if failed
        """
        video_logger = None

        try:
            logger.info(f"=" * 80)
            logger.info(f"Starting pipeline for: {youtube_url}")
            logger.info(f"=" * 80)

            # Stage 1: Download video
            logger.info("STAGE 1: Downloading video...")
            video_metadata = self.downloader.download(youtube_url)
            video_id = video_metadata['video_id']
            upload_date = video_metadata['upload_date']
            year_month = f"{upload_date[:4]}-{upload_date[4:6]}"

            # Set up video-specific logger
            video_logger = get_video_logger(video_id)
            video_logger.info(f"Processing video: {video_id}")
            video_logger.info(f"Title: {video_metadata['title']}")

            # Stage 2: Subtitle/Transcription
            logger.info("STAGE 2: Processing subtitles/transcription...")

            # Try to download subtitles first
            subtitle_file = None
            if video_metadata['has_subtitles']:
                subtitle_file = self.downloader.download_subtitles(
                    youtube_url,
                    video_id,
                    language='en'
                )

            english_transcript = self.transcriber.process(
                video_metadata,
                subtitle_file=subtitle_file
            )

            video_logger.info(f"Transcript source: {english_transcript['source']}")
            video_logger.info(f"Segments: {english_transcript['segment_count']}")

            # Stage 3: Translation
            logger.info("STAGE 3: Translating to Chinese...")

            chinese_transcript = self.translator.translate(
                english_transcript,
                video_id,
                year_month
            )

            video_logger.info(f"Translation completed: {chinese_transcript['segment_count']} segments")

            # Stage 4: Video processing (burn subtitles)
            logger.info("STAGE 4: Burning subtitles into video...")

            video_processing = self.video_processor.burn_subtitles(
                video_metadata['video_path'],
                chinese_transcript['srt_file_path'],
                video_id,
                year_month
            )

            video_logger.info(f"Video processing completed")
            video_logger.info(f"Output: {video_processing['subtitled_video_path']}")

            # Stage 5: Content analysis
            logger.info("STAGE 5: Generating summary and insights...")

            analysis = self.analyzer.analyze(chinese_transcript, video_metadata)

            video_logger.info(f"Analysis completed")
            video_logger.info(f"Topics: {', '.join(analysis['topics'])}")

            # Stage 6: Save metadata
            logger.info("STAGE 6: Saving metadata...")

            metadata = self.storage.build_metadata(
                video_metadata,
                english_transcript,
                chinese_transcript,
                video_processing,
                analysis
            )

            json_path = self.storage.save_metadata(video_id, year_month, metadata)

            video_logger.info(f"Metadata saved to: {json_path}")

            # Stage 7: Publishing
            logger.info("STAGE 7: Publishing to platforms...")

            publishing_results = self.publisher.publish(
                video_processing['subtitled_video_path'],
                video_metadata,
                analysis
            )

            # Update publishing status
            for platform, result in publishing_results.items():
                status = result.get('status', 'failed')
                post_id = result.get('post_id') or result.get('video_id')
                url = result.get('url')

                self.storage.update_publishing_status(
                    video_id,
                    year_month,
                    platform,
                    status,
                    post_id=post_id,
                    url=url
                )

            video_logger.info(f"Publishing completed")

            # Final summary
            logger.info("=" * 80)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info(f"Video ID: {video_id}")
            logger.info(f"Title: {video_metadata['title']}")
            logger.info(f"Metadata: {json_path}")
            logger.info(f"Subtitled Video: {video_processing['subtitled_video_path']}")
            logger.info("=" * 80)

            return json_path

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            if video_logger:
                video_logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Z AI Knowledge Distillery Platform - Process YouTube videos"
    )

    parser.add_argument(
        'url',
        type=str,
        help='YouTube video URL'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file'
    )

    args = parser.parse_args()

    # Create and run pipeline
    try:
        pipeline = Pipeline(config_path=args.config)
        result = pipeline.process_video(args.url)

        if result:
            print(f"\n✓ Pipeline completed successfully!")
            print(f"Metadata saved to: {result}")
            sys.exit(0)
        else:
            print(f"\n✗ Pipeline failed")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Pipeline error: {str(e)}")
        logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
