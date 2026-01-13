import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Resume endpoints
export const resumeApi = {
    upload: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/resumes/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
    list: () => api.get('/resumes/'),
    get: (id) => api.get(`/resumes/${id}`),
    delete: (id) => api.delete(`/resumes/${id}`),
    getSkills: (id) => api.get(`/resumes/${id}/skills`),
};

// Job endpoints
export const jobApi = {
    list: (params) => api.get('/jobs/', { params }),
    get: (id) => api.get(`/jobs/${id}`),
    search: (query) => api.get('/jobs/', { params: { query } }),
    searchBySkills: (skills) => api.get('/jobs/search/skills', { params: { skills } }),
};

// Match endpoints
export const matchApi = {
    calculate: (resumeId, jobId) => api.post('/matches/calculate', { resume_id: resumeId, job_id: jobId }),
    getForResume: (resumeId) => api.get(`/matches/resume/${resumeId}`),
    get: (id) => api.get(`/matches/${id}`),
    explain: (id) => api.get(`/matches/${id}/explain`),
};

// Recommendation endpoints
export const recommendationApi = {
    generate: (resumeId, filters = {}, limit = 5) =>
        api.post('/recommendations/generate', { resume_id: resumeId, filters, limit }),
    getForResume: (resumeId) => api.get(`/recommendations/resume/${resumeId}`),
    getHistory: (limit = 10) => api.get('/recommendations/history', { params: { limit } }),
};

export default api;
