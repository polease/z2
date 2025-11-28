"""
Pipeline runner - integrates existing pipeline with job queue
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

# Add parent directory to path for importing existing modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.downloader import VideoDownloader
from src.transcriber import SubtitleProcessor
from src.translator import Translator
from src.video_processor import VideoProcessor
from src.analyzer import ContentAnalyzer
from src.publisher import Publisher
from src.utils.logger import get_app_logger

from ..database import SessionLocal
from ..services.job_service import JobService
from ..services.websocket_manager import manager


class PipelineRunner:
    """Run the complete pipeline for a job"""

    def __init__(self, job_id: int, youtube_url: str):
        self.job_id = job_id
        self.youtube_url = youtube_url
        self.video_id = None
        self.cancelled = False
        self.logger = get_app_logger()

    async def run(self):
        """Execute the complete pipeline"""
        db = SessionLocal()

        try:
            await self.update_status(db, "DOWNLOADING", 10)

            # Stage 1: Download video
            self.log_info(db, "Starting video download...", "downloading")
            downloader = VideoDownloader()
            result = await asyncio.to_thread(
                downloader.download,
                self.youtube_url
            )

            if self.check_cancelled():
                return

            self.video_id = result['video_id']
            year_month = result['year_month']

            # Save metadata
            await self.save_metadata(db, result)
            self.log_info(db, f"Video downloaded: {result['video_path']}", "downloading")
            await self.update_status(db, "TRANSCRIBING", 25)

            # Stage 2: Transcribe
            self.log_info(db, "Starting transcription...", "transcribing")
            transcriber = SubtitleProcessor()
            transcripts = await asyncio.to_thread(
                transcriber.process,
                result['video_path'],
                self.video_id,
                year_month
            )

            if self.check_cancelled():
                return

            self.log_info(db, "Transcription completed", "transcribing")
            await self.update_status(db, "TRANSLATING", 40)

            # Stage 3: Translate
            self.log_info(db, "Starting translation...", "translating")
            translator = Translator()
            translation = await asyncio.to_thread(
                translator.translate,
                transcripts['full_text'],
                transcripts['segments'],
                self.video_id,
                year_month
            )

            if self.check_cancelled():
                return

            self.log_info(db, "Translation completed", "translating")
            await self.update_status(db, "PROCESSING_VIDEO", 60)

            # Stage 4: Process video (burn subtitles)
            self.log_info(db, "Burning subtitles into video...", "processing_video")
            processor = VideoProcessor()
            processed = await asyncio.to_thread(
                processor.burn_subtitles,
                result['video_path'],
                translation['chinese_srt_path'],
                self.video_id,
                year_month
            )

            if self.check_cancelled():
                return

            # Save file records
            await self.save_files(db, result, translation, processed)
            self.log_info(db, "Video processing completed", "processing_video")
            await self.update_status(db, "ANALYZING", 75)

            # Stage 5: Analyze content
            self.log_info(db, "Analyzing content...", "analyzing")
            analyzer = ContentAnalyzer()
            analysis = await asyncio.to_thread(
                analyzer.analyze,
                translation['full_text']
            )

            if self.check_cancelled():
                return

            # Save analysis
            await self.save_analysis(db, analysis)
            self.log_info(db, "Content analysis completed", "analyzing")
            await self.update_status(db, "PUBLISHING", 85)

            # Stage 6: Publish
            self.log_info(db, "Publishing to platforms...", "publishing")
            publisher = Publisher()
            publishing_results = await asyncio.to_thread(
                publisher.publish,
                processed['subtitled_video_path'],
                result,
                analysis
            )

            if self.check_cancelled():
                return

            # Save publishing results
            await self.save_publishing(db, publishing_results)
            self.log_info(db, "Publishing completed", "publishing")

            # Mark as completed
            await self.update_status(db, "COMPLETED", 100)
            self.log_info(db, "Pipeline completed successfully", "completed")

        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.log_error(db, error_msg, "error")

            JobService.update_job_status(
                db,
                self.job_id,
                status="FAILED",
                error_message=str(e)
            )

            # Broadcast error status
            job = JobService.get_job_by_id(db, self.job_id)
            await manager.broadcast_status({
                "job_uuid": str(job.job_uuid),
                "status": "FAILED",
                "progress": job.progress,
                "stage": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            })

        finally:
            db.close()

    def check_cancelled(self) -> bool:
        """Check if job was cancelled"""
        db = SessionLocal()
        try:
            job = JobService.get_job_by_id(db, self.job_id)
            if job and job.cancelled:
                self.cancelled = True
                self.log_info(db, "Job cancelled by user", "cancelled")
                return True
            return False
        finally:
            db.close()

    async def update_status(self, db, status: str, progress: int):
        """Update job status and broadcast via WebSocket"""
        job = JobService.update_job_status(db, self.job_id, status, progress)

        # Broadcast via WebSocket
        await manager.broadcast_status({
            "job_uuid": str(job.job_uuid),
            "status": status,
            "progress": progress,
            "stage": status.lower(),
            "timestamp": datetime.utcnow().isoformat()
        })

    def log_info(self, db, message: str, stage: str):
        """Log info message"""
        self.logger.info(message)
        JobService.add_log(db, self.job_id, "INFO", message, stage)

        # Send via WebSocket
        asyncio.create_task(manager.send_log(self.job_id, {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "stage": stage,
            "message": message
        }))

    def log_error(self, db, message: str, stage: str):
        """Log error message"""
        self.logger.error(message)
        JobService.add_log(db, self.job_id, "ERROR", message, stage)

        # Send via WebSocket
        asyncio.create_task(manager.send_log(self.job_id, {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "ERROR",
            "stage": stage,
            "message": message
        }))

    async def save_metadata(self, db, result: dict):
        """Save video metadata to database"""
        metadata = result.get('metadata', {})
        JobService.add_job_metadata(db, self.job_id, {
            "video_title": metadata.get('title'),
            "channel_name": metadata.get('channel'),
            "channel_id": metadata.get('channel_id'),
            "upload_date": metadata.get('upload_date'),
            "duration": metadata.get('duration'),
            "view_count": metadata.get('view_count'),
            "like_count": metadata.get('like_count'),
            "thumbnail_url": metadata.get('thumbnail_url'),
            "description": metadata.get('description')
        })

        # Update video_id in job
        job = JobService.get_job_by_id(db, self.job_id)
        if job and not job.video_id:
            job.video_id = result['video_id']
            db.commit()

    async def save_files(self, db, download_result: dict, translation: dict, processed: dict):
        """Save file records to database"""
        # Original video
        video_path = download_result['video_path']
        video_size = os.path.getsize(video_path) / (1024 * 1024) if os.path.exists(video_path) else None
        JobService.add_file(db, self.job_id, "original_video", video_path, video_size)

        # Subtitled video
        subtitled_path = processed['subtitled_video_path']
        subtitled_size = processed.get('output_size_mb')
        JobService.add_file(db, self.job_id, "subtitled_video", subtitled_path, subtitled_size)

        # English SRT
        JobService.add_file(db, self.job_id, "english_srt", translation['english_srt_path'])

        # Chinese SRT
        JobService.add_file(db, self.job_id, "chinese_srt", translation['chinese_srt_path'])

    async def save_analysis(self, db, analysis: dict):
        """Save content analysis to database"""
        JobService.add_analysis(db, self.job_id, {
            "summary": analysis.get('summary'),
            "key_insights": analysis.get('key_insights'),
            "highlights": analysis.get('highlights'),
            "topics": analysis.get('topics')
        })

    async def save_publishing(self, db, results: dict):
        """Save publishing results to database"""
        for platform, result in results.items():
            JobService.add_publishing_status(
                db,
                self.job_id,
                platform=platform,
                status=result.get('status', 'unknown'),
                post_id=result.get('post_id'),
                url=result.get('url'),
                error_message=result.get('error') or result.get('message')
            )
