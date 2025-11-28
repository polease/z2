"""
REST API endpoints for job management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ..database import get_db
from ..schemas import (
    JobCreate,
    JobResponse,
    JobDetailResponse,
    JobListResponse,
    JobLogResponse,
    StatsResponse
)
from ..services.job_service import JobService
from ..services.job_queue import job_queue_manager
from ..utils.validators import is_valid_youtube_url

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=201)
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new job

    - Validates YouTube URL
    - Creates job record in database
    - Enqueues job for processing
    """
    # Validate YouTube URL
    if not is_valid_youtube_url(job_data.youtube_url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    # Create job
    job = JobService.create_job(db, job_data)

    # Enqueue job for processing
    await job_queue_manager.enqueue(job.id, job.youtube_url)

    return job


@router.get("", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List all jobs with pagination and filtering

    - **skip**: Number of jobs to skip (for pagination)
    - **limit**: Maximum number of jobs to return
    - **status**: Filter by job status (optional)
    """
    jobs, total = JobService.get_jobs(db, skip=skip, limit=limit, status=status)

    return JobListResponse(
        jobs=jobs,
        total=total,
        limit=limit,
        offset=skip
    )


@router.get("/{job_uuid}", response_model=JobDetailResponse)
async def get_job(
    job_uuid: UUID,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific job

    Includes metadata, files, logs, analysis, and publishing status
    """
    job = JobService.get_job_by_uuid(db, job_uuid)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.delete("/{job_uuid}")
async def cancel_job(
    job_uuid: UUID,
    db: Session = Depends(get_db)
):
    """
    Cancel a running job

    Cannot cancel jobs that are already completed, failed, or cancelled
    """
    job = JobService.get_job_by_uuid(db, job_uuid)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    cancelled_job = JobService.cancel_job(db, job.id)

    if not cancelled_job:
        raise HTTPException(
            status_code=400,
            detail="Job cannot be cancelled (already completed, failed, or cancelled)"
        )

    # Signal the running job to stop
    await job_queue_manager.cancel_job(job.id)

    return {"message": "Job cancelled successfully", "job_uuid": str(job_uuid)}


@router.get("/{job_uuid}/logs", response_model=list[JobLogResponse])
async def get_job_logs(
    job_uuid: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """
    Get logs for a specific job

    Returns paginated log entries in chronological order
    """
    job = JobService.get_job_by_uuid(db, job_uuid)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    logs = JobService.get_logs(db, job.id, skip=skip, limit=limit)

    return logs
