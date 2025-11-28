// API client
import axios from 'axios';
import { Job, JobDetail, Stats, JobLog } from './types';

const api = axios.create({
  baseURL: '/api',
});

export const jobsApi = {
  // Create a new job
  create: async (youtubeUrl: string): Promise<Job> => {
    const response = await api.post('/jobs', { youtube_url: youtubeUrl });
    return response.data;
  },

  // List all jobs
  list: async (): Promise<Job[]> => {
    const response = await api.get('/jobs');
    return response.data.jobs;
  },

  // Get job details
  get: async (jobUuid: string): Promise<JobDetail> => {
    const response = await api.get(`/jobs/${jobUuid}`);
    return response.data;
  },

  // Get job logs
  getLogs: async (jobUuid: string): Promise<JobLog[]> => {
    const response = await api.get(`/jobs/${jobUuid}/logs`);
    return response.data;
  },

  // Cancel job
  cancel: async (jobUuid: string): Promise<void> => {
    await api.delete(`/jobs/${jobUuid}`);
  },
};

export const statsApi = {
  // Get statistics
  get: async (): Promise<Stats> => {
    const response = await api.get('/stats');
    return response.data;
  },
};
