// API service for handling backend communication with proper CORS and auth setup
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Default fetch configuration with token auth
const defaultFetchConfig = {
  headers: {
    'Content-Type': 'application/json',
  },
};

// Get CSRF token from cookies (if using CSRF protection)
const getCSRFToken = () => {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  return cookieValue;
};

// API helper function with error handling
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Get auth token
  const token = localStorage.getItem('authToken');
  
  // Merge default config with provided options
  const config = {
    ...defaultFetchConfig,
    ...options,
    headers: {
      ...defaultFetchConfig.headers,
      ...options.headers,
    },
  };

  // Add auth token if available
  if (token) {
    config.headers['Authorization'] = `Token ${token}`;
  }

  // Add CSRF token for unsafe methods
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(config.method?.toUpperCase())) {
    const csrfToken = getCSRFToken();
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
  }

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorData}`);
    }
    
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return await response.text();
  } catch (error) {
    console.error(`API Request failed for ${endpoint}:`, error);
    throw error;
  }
};

// Topic API endpoints
export const topicAPI = {
  // GET /api/topics/ - List all topics with chat-generated questions
  list: () => apiRequest('/topics/'),
};

// Question API endpoints  
export const questionAPI = {
  // GET /api/questions/?is_generated=true - List chat-generated questions
  list: (params = {}) => {
    const queryParams = new URLSearchParams({ is_generated: 'true', ...params });
    return apiRequest(`/questions/?${queryParams}`);
  },
};

// Exam Session API endpoints
export const examSessionAPI = {
  // POST /api/exam-sessions/ - Create new exam session
  create: (data) => apiRequest('/exam-sessions/', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  // GET /api/exam-sessions/list/ - List exam sessions
  list: () => apiRequest('/exam-sessions/list/'),
  
  // GET /api/exam-sessions/{id}/ - Get specific exam session
  get: (id) => apiRequest(`/exam-sessions/${id}/`),
  
  // DELETE /api/exam-sessions/{id}/delete/ - Delete exam session
  delete: (id) => apiRequest(`/exam-sessions/${id}/delete/`, {
    method: 'DELETE',
  }),
};

// Default export with all APIs
const api = {
  topics: topicAPI,
  questions: questionAPI,
  examSessions: examSessionAPI,
};

export default api;
