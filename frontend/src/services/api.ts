import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// #region agent log
fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:3',message:'API client initialized',data:{baseURL:`${API_BASE_URL}/api`,envUrl:import.meta.env.VITE_API_URL},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'D'})}).catch(()=>{});
// #endregion

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token (Phase 5)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:13',message:'API request interceptor',data:{url:config.url,hasToken:!!token,method:config.method},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'E'})}).catch(()=>{});
  // #endregion
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/6ab49e72-b272-4456-a3cc-16544060033b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:22',message:'API response error',data:{status:error.response?.status,url:error.config?.url,message:error.message},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'G'})}).catch(()=>{});
    // #endregion
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
