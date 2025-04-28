import axios from 'axios';

// Create an axios instance with the base URL for all API calls
export const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000, // Increased timeout for potentially slow API operations
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for authentication if needed
api.interceptors.request.use(
  (config) => {
    // You can add auth token here if needed
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

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle API errors globally
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('API Error:', error.response.data);
      
      // Handle authentication errors
      if (error.response.status === 401) {
        // Redirect to login or refresh token
        localStorage.removeItem('token');
        // window.location.href = '/login';
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Network Error:', error.request);
      
      // Special handling for cache stats errors to prevent console spam
      if (error.config && error.config.url && error.config.url.includes('/cache/stats')) {
        console.warn('Cache stats not available - this is expected during development');
        // Return empty stats to prevent UI errors
        return Promise.resolve({ data: { hits: 0, misses: 0, items: 0, total_queries: 0, total_articles: 0, cache_size_bytes: 0 } });
      }
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Request Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);
