// TypeScript types for the application

export interface Job {
  id: number;
  job_uuid: string;
  youtube_url: string;
  video_id: string | null;
  status: string;
  progress: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  cancelled: boolean;
}

export interface JobMetadata {
  video_title: string | null;
  channel_name: string | null;
  duration: number | null;
}

export interface JobDetail extends Job {
  job_metadata: JobMetadata | null;
}

export interface Stats {
  total_jobs: number;
  completed: number;
  failed: number;
  running: number;
  pending: number;
  cancelled: number;
  avg_duration_minutes: number | null;
}

export interface JobLog {
  id: number;
  timestamp: string;
  level: string;
  message: string;
  stage: string | null;
}
