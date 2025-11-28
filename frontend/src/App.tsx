import React, { useState, useEffect } from 'react';
import { jobsApi, statsApi } from './api';
import { Job, Stats } from './types';
import './App.css';

function App() {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchJobs();
    fetchStats();
    const interval = setInterval(() => {
      fetchJobs();
      fetchStats();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchJobs = async () => {
    try {
      const data = await jobsApi.list();
      setJobs(data);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await statsApi.get();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!youtubeUrl.trim()) return;
    setLoading(true);
    setError('');
    try {
      await jobsApi.create(youtubeUrl);
      setYoutubeUrl('');
      fetchJobs();
      fetchStats();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create job');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED': return '#4caf50';
      case 'FAILED': return '#f44336';
      case 'CANCELLED': return '#9e9e9e';
      case 'PENDING': return '#ff9800';
      default: return '#2196f3';
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎬 Z2 AI Knowledge Distillery</h1>
        <p>YouTube Video Processing Pipeline</p>
      </header>

      {stats && (
        <div className="stats-container">
          <div className="stat-card">
            <div className="stat-value">{stats.total_jobs}</div>
            <div className="stat-label">Total Jobs</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.running}</div>
            <div className="stat-label">Running</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.completed}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.failed}</div>
            <div className="stat-label">Failed</div>
          </div>
        </div>
      )}

      <div className="form-container">
        <h2>Submit New Job</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Enter YouTube URL..."
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            className="url-input"
            disabled={loading}
          />
          <button type="submit" disabled={loading} className="submit-button">
            {loading ? 'Submitting...' : 'Process Video'}
          </button>
        </form>
        {error && <div className="error-message">{error}</div>}
      </div>

      <div className="jobs-container">
        <h2>Recent Jobs</h2>
        {jobs.length === 0 ? (
          <p className="no-jobs">No jobs yet. Submit a YouTube URL to get started!</p>
        ) : (
          <div className="jobs-list">
            {jobs.map((job) => (
              <div key={job.id} className="job-card">
                <div className="job-header">
                  <div className="job-title">
                    <strong>{job.video_id || 'Processing...'}</strong>
                  </div>
                  <div className="job-status" style={{ backgroundColor: getStatusColor(job.status) }}>
                    {job.status}
                  </div>
                </div>
                <div className="job-url">{job.youtube_url}</div>
                <div className="job-progress">
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${job.progress}%` }}></div>
                  </div>
                  <div className="progress-text">{job.progress}%</div>
                </div>
                <div className="job-footer">
                  <span className="job-time">Created: {formatDate(job.created_at)}</span>
                  <span className="job-id">ID: {job.job_uuid.slice(0, 8)}...</span>
                </div>
                {job.error_message && (
                  <div className="error-message">{job.error_message}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <footer className="App-footer">
        <p>Backend API: <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">http://localhost:8000/docs</a></p>
      </footer>
    </div>
  );
}

export default App;
