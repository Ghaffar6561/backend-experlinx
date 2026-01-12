// api.js - API service for connecting to the backend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create a base API request function
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Add token to headers if available
  const token = localStorage.getItem('token');
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, config);
    
    // If response is not JSON, return as text
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      
      // Handle API response format (based on backend structure)
      if (response.ok) {
        return { success: true, data: data.data || data };
      } else {
        return { success: false, error: data.error || data.detail || 'Request failed' };
      }
    } else {
      // For non-JSON responses, return text
      const text = await response.text();
      if (response.ok) {
        return { success: true, data: text };
      } else {
        return { success: false, error: text };
      }
    }
  } catch (error) {
    console.error('API request error:', error);
    return { success: false, error: error.message || 'Network error' };
  }
};

// Authentication API functions
export const authAPI = {
  register: (userData) => 
    apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    }),
    
  login: (credentials) => 
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    }),
    
  refresh: (refreshToken) => 
    apiRequest('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken })
    }),
    
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  }
};

// User API functions
export const userAPI = {
  getProfile: () => 
    apiRequest('/users/me'),
    
  updateProfile: (updateData) => 
    apiRequest('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(updateData)
    }),
    
  getApiKeys: () => 
    apiRequest('/users/me/api-keys'),
    
  createApiKey: (name) => 
    apiRequest('/users/me/api-keys', {
      method: 'POST',
      body: JSON.stringify({ name })
    }),
    
  revokeApiKey: (keyId) => 
    apiRequest(`/users/me/api-keys/${keyId}`, {
      method: 'DELETE'
    })
};

// Tool API functions
export const toolAPI = {
  getTools: () => 
    apiRequest('/tools'),
    
  getTool: (toolId) => 
    apiRequest(`/tools/${toolId}`),
    
  invokeTool: (toolId, inputData) => 
    apiRequest(`/tools/${toolId}/invoke`, {
      method: 'POST',
      body: JSON.stringify(inputData)
    })
};

// Subscription API functions
export const subscriptionAPI = {
  getPlans: () => 
    apiRequest('/subscriptions/plans'),
    
  getCurrent: () => 
    apiRequest('/subscriptions/current'),
    
  subscribe: (planId) => 
    apiRequest('/subscriptions', {
      method: 'POST',
      body: JSON.stringify({ plan_id: planId })
    })
};

// Usage API functions
export const usageAPI = {
  getHistory: (params = {}) => {
    const queryParams = new URLSearchParams(params).toString();
    return apiRequest(`/usage/history${queryParams ? `?${queryParams}` : ''}`);
  },
  
  getSummary: () => 
    apiRequest('/usage/summary')
};

export default {
  authAPI,
  userAPI,
  toolAPI,
  subscriptionAPI,
  usageAPI
};