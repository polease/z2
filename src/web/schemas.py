"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Job schemas
class JobCreate(BaseModel):
    youtube_url: str = Field(..., description="YouTube video URL")


class JobMetadataResponse(BaseModel):
    video_title: Optional[str]
    channel_name: Optional[str]
    channel_id: Optional[str]
    upload_date: Optional[str]
    duration: Optional[int]
    view_count: Optional[int]
    like_count: Optional[int]
    thumbnail_url: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True


class JobFileResponse(BaseModel):
    file_type: str
    file_path: str
    file_size_mb: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class JobAnalysisResponse(BaseModel):
    summary: Optional[str]
    key_insights: Optional[List]
    highlights: Optional[List]
    topics: Optional[List]

    class Config:
        from_attributes = True


class JobPublishingResponse(BaseModel):
    platform: str
    status: str
    published_at: Optional[datetime]
    post_id: Optional[str]
    url: Optional[str]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: int
    job_uuid: UUID
    youtube_url: str
    video_id: Optional[str]
    status: str
    progress: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    cancelled: bool

    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    job_metadata: Optional[JobMetadataResponse]
    files: List[JobFileResponse]
    analysis: Optional[JobAnalysisResponse]
    publishing: List[JobPublishingResponse]

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    limit: int
    offset: int


class JobLogResponse(BaseModel):
    id: int
    timestamp: datetime
    level: str
    message: str
    stage: Optional[str]

    class Config:
        from_attributes = True


# Statistics schema
class StatsResponse(BaseModel):
    total_jobs: int
    completed: int
    failed: int
    running: int
    pending: int
    cancelled: int
    avg_duration_minutes: Optional[float]


# WebSocket message schemas
class StatusUpdateMessage(BaseModel):
    job_uuid: UUID
    status: str
    progress: int
    stage: Optional[str]
    timestamp: datetime


class LogMessage(BaseModel):
    timestamp: datetime
    level: str
    stage: Optional[str]
    message: str
