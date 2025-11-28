"""
SQLAlchemy models for database tables
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, Numeric, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
from .database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)
    youtube_url = Column(Text, nullable=False)
    video_id = Column(String(20), index=True)
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    progress = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    started_at = Column(TIMESTAMP, nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)
    error_message = Column(Text, nullable=True)
    cancelled = Column(Boolean, default=False)

    # Relationships
    job_metadata = relationship("JobMetadata", back_populates="job", uselist=False, cascade="all, delete-orphan")
    logs = relationship("JobLog", back_populates="job", cascade="all, delete-orphan")
    files = relationship("JobFile", back_populates="job", cascade="all, delete-orphan")
    analysis = relationship("JobAnalysis", back_populates="job", uselist=False, cascade="all, delete-orphan")
    publishing = relationship("JobPublishing", back_populates="job", cascade="all, delete-orphan")


class JobMetadata(Base):
    __tablename__ = "job_metadata"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    video_title = Column(Text)
    channel_name = Column(Text)
    channel_id = Column(Text)
    upload_date = Column(Text)
    duration = Column(Integer)
    view_count = Column(Integer)
    like_count = Column(Integer)
    thumbnail_url = Column(Text)
    description = Column(Text)

    # Relationship
    job = relationship("Job", back_populates="job_metadata")


class JobLog(Base):
    __tablename__ = "job_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    level = Column(String(20))
    message = Column(Text)
    stage = Column(String(50))

    # Relationship
    job = relationship("Job", back_populates="logs")


class JobFile(Base):
    __tablename__ = "job_files"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    file_type = Column(String(50))
    file_path = Column(Text)
    file_size_mb = Column(Numeric(10, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship
    job = relationship("Job", back_populates="files")


class JobAnalysis(Base):
    __tablename__ = "job_analysis"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), unique=True)
    summary = Column(Text)
    key_insights = Column(JSONB)
    highlights = Column(JSONB)
    topics = Column(JSONB)

    # Relationship
    job = relationship("Job", back_populates="analysis")


class JobPublishing(Base):
    __tablename__ = "job_publishing"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), index=True)
    platform = Column(String(50))
    status = Column(String(50))
    published_at = Column(TIMESTAMP, nullable=True)
    post_id = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationship
    job = relationship("Job", back_populates="publishing")
