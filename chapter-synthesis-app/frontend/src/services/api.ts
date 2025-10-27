import axios from 'axios';

const API_BASE_URL = '/api';

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/auth/login', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data: any) => api.post('/auth/register', data),
  getCurrentUser: () => api.get('/auth/me'),
  updatePreferences: (preferences: any) => api.put('/auth/me/preferences', preferences),
};

// Documents API
export const documentsAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: (skip = 0, limit = 50) => api.get(`/documents/?skip=${skip}&limit=${limit}`),
  get: (id: number) => api.get(`/documents/${id}`),
  getSections: (id: number) => api.get(`/documents/${id}/sections`),
  delete: (id: number) => api.delete(`/documents/${id}`),
};

// Chapters API
export const chaptersAPI = {
  generate: (data: any) => api.post('/chapters/generate', data),
  list: (skip = 0, limit = 50, status?: string) => {
    let url = `/chapters/?skip=${skip}&limit=${limit}`;
    if (status) url += `&status=${status}`;
    return api.get(url);
  },
  get: (id: number) => api.get(`/chapters/${id}`),
  getContent: (id: number, version?: string) => {
    let url = `/chapters/${id}/content`;
    if (version) url += `?version_number=${version}`;
    return api.get(url);
  },
  getVersions: (id: number) => api.get(`/chapters/${id}/versions`),
  rollback: (id: number, versionId: number) =>
    api.post(`/chapters/${id}/rollback`, { target_version_id: versionId }),
  getGaps: (id: number) => api.get(`/chapters/${id}/gaps`),
  delete: (id: number) => api.delete(`/chapters/${id}`),
};

// Jobs API
export const jobsAPI = {
  list: (skip = 0, limit = 50, jobType?: string, status?: string) => {
    let url = `/jobs/?skip=${skip}&limit=${limit}`;
    if (jobType) url += `&job_type=${jobType}`;
    if (status) url += `&status=${status}`;
    return api.get(url);
  },
  get: (jobId: string) => api.get(`/jobs/${jobId}`),
  getStages: (jobId: string) => api.get(`/jobs/${jobId}/stages`),
  cancel: (jobId: string) => api.delete(`/jobs/${jobId}`),
};

// Dashboard API
export const dashboardAPI = {
  getMetrics: () => api.get('/dashboard/metrics'),
  getRecentActivity: (limit = 20) => api.get(`/dashboard/recent-activity?limit=${limit}`),
  getPerformance: () => api.get('/dashboard/performance'),
  getCostAnalysis: () => api.get('/dashboard/cost-analysis'),
};
