"""
Job service - business logic for job management
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from ..models import Job, JobMetadata, JobLog, JobFile, JobAnalysis, JobPublishing
from ..schemas import JobCreate, JobResponse, JobDetailResponse, StatsResponse
from ..utils.validators import extract_youtube_video_id


class JobService:
    """Service for managing jobs"""

    @staticmethod
    def create_job(db: Session, job_data: JobCreate) -> Job:
        """Create a new job"""
        video_id = extract_youtube_video_id(job_data.youtube_url)

        job = Job(
            youtube_url=job_data.youtube_url,
            video_id=video_id,
            status="PENDING",
            progress=0
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_job_by_id(db: Session, job_id: int) -> Optional[Job]:
        """Get job by ID"""
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def get_job_by_uuid(db: Session, job_uuid: UUID) -> Optional[Job]:
        """Get job by UUID"""
        return db.query(Job).filter(Job.job_uuid == job_uuid).first()

    @staticmethod
    def get_jobs(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None
    ) -> tuple[List[Job], int]:
        """Get list of jobs with pagination and filtering"""
        query = db.query(Job)

        if status:
            query = query.filter(Job.status == status)

        total = query.count()
        jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

        return jobs, total

    @staticmethod
    def update_job_status(
        db: Session,
        job_id: int,
        status: str,
        progress: int = None,
        error_message: str = None
    ) -> Optional[Job]:
        """Update job status and progress"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        job.status = status
        if progress is not None:
            job.progress = progress
        if error_message:
            job.error_message = error_message

        # Update timestamps
        if status != "PENDING" and not job.started_at:
            job.started_at = datetime.utcnow()

        if status in ["COMPLETED", "FAILED", "CANCELLED"]:
            job.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def cancel_job(db: Session, job_id: int) -> Optional[Job]:
        """Cancel a job"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        if job.status in ["COMPLETED", "FAILED", "CANCELLED"]:
            return None  # Already finished

        job.cancelled = True
        job.status = "CANCELLED"
        job.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def add_job_metadata(db: Session, job_id: int, metadata: dict) -> JobMetadata:
        """Add or update job metadata"""
        existing = db.query(JobMetadata).filter(JobMetadata.job_id == job_id).first()

        if existing:
            for key, value in metadata.items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            job_metadata = JobMetadata(job_id=job_id, **metadata)
            db.add(job_metadata)
            db.commit()
            db.refresh(job_metadata)
            return job_metadata

    @staticmethod
    def add_log(
        db: Session,
        job_id: int,
        level: str,
        message: str,
        stage: Optional[str] = None
    ) -> JobLog:
        """Add a log entry"""
        log = JobLog(
            job_id=job_id,
            level=level,
            message=message,
            stage=stage
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_logs(db: Session, job_id: int, skip: int = 0, limit: int = 1000) -> List[JobLog]:
        """Get logs for a job"""
        return (
            db.query(JobLog)
            .filter(JobLog.job_id == job_id)
            .order_by(JobLog.timestamp.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def add_file(
        db: Session,
        job_id: int,
        file_type: str,
        file_path: str,
        file_size_mb: float = None
    ) -> JobFile:
        """Add a file record"""
        job_file = JobFile(
            job_id=job_id,
            file_type=file_type,
            file_path=file_path,
            file_size_mb=file_size_mb
        )
        db.add(job_file)
        db.commit()
        db.refresh(job_file)
        return job_file

    @staticmethod
    def add_analysis(db: Session, job_id: int, analysis: dict) -> JobAnalysis:
        """Add or update job analysis"""
        existing = db.query(JobAnalysis).filter(JobAnalysis.job_id == job_id).first()

        if existing:
            for key, value in analysis.items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            job_analysis = JobAnalysis(job_id=job_id, **analysis)
            db.add(job_analysis)
            db.commit()
            db.refresh(job_analysis)
            return job_analysis

    @staticmethod
    def add_publishing_status(
        db: Session,
        job_id: int,
        platform: str,
        status: str,
        post_id: str = None,
        url: str = None,
        error_message: str = None
    ) -> JobPublishing:
        """Add publishing status"""
        publishing = JobPublishing(
            job_id=job_id,
            platform=platform,
            status=status,
            post_id=post_id,
            url=url,
            error_message=error_message,
            published_at=datetime.utcnow() if status == "success" else None
        )
        db.add(publishing)
        db.commit()
        db.refresh(publishing)
        return publishing

    @staticmethod
    def get_statistics(db: Session) -> StatsResponse:
        """Get job statistics"""
        total_jobs = db.query(Job).count()
        completed = db.query(Job).filter(Job.status == "COMPLETED").count()
        failed = db.query(Job).filter(Job.status == "FAILED").count()
        running = db.query(Job).filter(
            and_(
                Job.status.notin_(["PENDING", "COMPLETED", "FAILED", "CANCELLED"]),
                Job.cancelled == False
            )
        ).count()
        pending = db.query(Job).filter(Job.status == "PENDING").count()
        cancelled = db.query(Job).filter(Job.cancelled == True).count()

        # Calculate average duration for completed jobs
        avg_duration = db.query(
            func.avg(
                func.extract('epoch', Job.completed_at - Job.started_at) / 60
            )
        ).filter(
            and_(
                Job.status == "COMPLETED",
                Job.started_at.isnot(None),
                Job.completed_at.isnot(None)
            )
        ).scalar()

        return StatsResponse(
            total_jobs=total_jobs,
            completed=completed,
            failed=failed,
            running=running,
            pending=pending,
            cancelled=cancelled,
            avg_duration_minutes=float(avg_duration) if avg_duration else None
        )
