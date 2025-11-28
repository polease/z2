-- Z2 AI Knowledge Distillery Platform - Database Schema
-- PostgreSQL Database Schema for Web Dashboard

-- Create database (run this separately if needed)
-- CREATE DATABASE z2_platform;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS job_publishing CASCADE;
DROP TABLE IF EXISTS job_analysis CASCADE;
DROP TABLE IF EXISTS job_files CASCADE;
DROP TABLE IF EXISTS job_logs CASCADE;
DROP TABLE IF EXISTS job_metadata CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;

-- Main jobs table
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    job_uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    youtube_url TEXT NOT NULL,
    video_id VARCHAR(20),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    cancelled BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_video_id ON jobs(video_id);

-- Job metadata table
CREATE TABLE job_metadata (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    video_title TEXT,
    channel_name TEXT,
    channel_id TEXT,
    upload_date TEXT,
    duration INTEGER,
    view_count INTEGER,
    like_count INTEGER,
    thumbnail_url TEXT,
    description TEXT,
    UNIQUE(job_id)
);

CREATE INDEX idx_job_metadata_job_id ON job_metadata(job_id);

-- Job logs table
CREATE TABLE job_logs (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20),
    message TEXT,
    stage VARCHAR(50)
);

CREATE INDEX idx_job_logs_job_id ON job_logs(job_id, timestamp);

-- Job files table
CREATE TABLE job_files (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    file_type VARCHAR(50),
    file_path TEXT,
    file_size_mb DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_job_files_job_id ON job_files(job_id);

-- Job analysis table
CREATE TABLE job_analysis (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    summary TEXT,
    key_insights JSONB,
    highlights JSONB,
    topics JSONB,
    UNIQUE(job_id)
);

CREATE INDEX idx_job_analysis_job_id ON job_analysis(job_id);

-- Job publishing table
CREATE TABLE job_publishing (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    platform VARCHAR(50),
    status VARCHAR(50),
    published_at TIMESTAMP,
    post_id TEXT,
    url TEXT,
    error_message TEXT
);

CREATE INDEX idx_job_publishing_job_id ON job_publishing(job_id);

-- Create a view for job summaries
CREATE OR REPLACE VIEW job_summary AS
SELECT
    j.id,
    j.job_uuid,
    j.youtube_url,
    j.video_id,
    j.status,
    j.progress,
    j.created_at,
    j.started_at,
    j.completed_at,
    j.cancelled,
    jm.video_title,
    jm.channel_name,
    jm.duration
FROM jobs j
LEFT JOIN job_metadata jm ON j.id = jm.job_id
ORDER BY j.created_at DESC;
