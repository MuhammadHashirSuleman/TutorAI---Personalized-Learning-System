// API Service for Frontend-Backend Communication
class APIService {
  constructor() {
    // Hardcode the URL for debugging - React apps sometimes don't pick up env changes
    this.baseURL = 'http://127.0.0.1:8000/api';
    this.token = localStorage.getItem('access_token');
    console.log('🔧 API Service initialized with baseURL:', this.baseURL);
    console.log('🔧 Token found:', this.token ? 'Yes' : 'No');
  }

  // Method to refresh token from localStorage
  refreshTokenFromStorage() {
    this.token = localStorage.getItem('access_token');
    console.log('🔄 Token refreshed from storage:', this.token ? 'Present' : 'Missing');
  }

  // Helper method to get headers
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth && this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Helper method to handle responses
  async handleResponse(response, isRetry = false) {
    console.log('🔍 Handling response with status:', response.status);
    
    if (!response.ok) {
      if (response.status === 401 && !isRetry) {
        console.log('🔄 Unauthorized - attempting token refresh before logout');
        
        // Try to refresh token first
        try {
          await this.refreshToken();
          console.log('✅ Token refreshed successfully');
          return 'TOKEN_REFRESHED'; // Signal to retry the original request
        } catch (refreshError) {
          console.log('❌ Token refresh failed, logging out:', refreshError);
          // Only logout if refresh fails
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
          return;
        }
      } else if (response.status === 401 && isRetry) {
        console.log('❌ Second 401 after refresh - forcing logout');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return;
      }
      
      let errorMessage = 'API request failed';
      try {
        const error = await response.json();
        console.log('📋 Error response JSON:', error);
        
        // Handle Django REST Framework error format
        if (error.non_field_errors && Array.isArray(error.non_field_errors)) {
          errorMessage = error.non_field_errors[0];
        } else if (error.message) {
          errorMessage = error.message;
        } else if (error.error) {
          errorMessage = error.error;
        } else if (error.detail) {
          errorMessage = error.detail;
        } else {
          // If it's an object with field errors, create a readable message
          const fieldErrors = [];
          for (const [field, messages] of Object.entries(error)) {
            if (Array.isArray(messages)) {
              fieldErrors.push(`${field}: ${messages.join(', ')}`);
            } else if (typeof messages === 'string') {
              fieldErrors.push(`${field}: ${messages}`);
            }
          }
          if (fieldErrors.length > 0) {
            errorMessage = fieldErrors.join('; ');
          }
        }
      } catch (e) {
        console.log('⚠️ Could not parse error response as JSON:', e.message);
        // Response is not JSON, try to get text
        try {
          const errorText = await response.text();
          console.log('📋 Error response text:', errorText);
          errorMessage = errorText || response.statusText || errorMessage;
        } catch (textError) {
          console.log('⚠️ Could not get error text:', textError.message);
          errorMessage = response.statusText || errorMessage;
        }
      }
      
      console.log('❌ Throwing error:', errorMessage);
      throw new Error(errorMessage);
    }
    
    // Handle 204 No Content responses (like DELETE)
    if (response.status === 204) {
      console.log('✅ Response OK (204 No Content)');
      return null;
    }
    
    console.log('✅ Response OK, parsing JSON');
    return response.json();
  }

  // Authentication APIs
  async register(userData) {
    try {
      console.log('🚀 Making registration request to:', `${this.baseURL}/auth/register/`);
      console.log('📤 Request data:', userData);
      console.log('📤 Request headers:', this.getHeaders(false));
      
      const response = await fetch(`${this.baseURL}/auth/register/`, {
        method: 'POST',
        headers: this.getHeaders(false),
        body: JSON.stringify(userData),
      });
      
      console.log('📥 Response status:', response.status);
      console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        const errorText = await response.text();
        console.log('❌ Error response body:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      console.log('📥 Response data:', data);
      
      // Store tokens and user data
      if (data.tokens) {
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
        this.token = data.tokens.access;
      }
      
      return data;
    } catch (error) {
      console.error('Registration error:', error);
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Cannot connect to server. Please check if the backend is running.');
      }
      throw error;
    }
  }

  async login(credentials) {
    try {
      console.log('🚀 Making login request to:', `${this.baseURL}/auth/login/`);
      console.log('📤 Request credentials:', { email: credentials.email, password: '[HIDDEN]' });
      console.log('📤 Request headers:', this.getHeaders(false));
      
      const response = await fetch(`${this.baseURL}/auth/login/`, {
        method: 'POST',
        headers: this.getHeaders(false),
        body: JSON.stringify(credentials),
      });
      
      console.log('📥 Response status:', response.status);
      console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()));
      
      const data = await this.handleResponse(response);
      
      console.log('📥 Response data received:', { message: data.message, user: data.user?.email });
      
      // Store tokens and user data
      if (data.tokens) {
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));
        this.token = data.tokens.access;
        console.log('✅ Tokens stored successfully');
      }
      
      return data;
    } catch (error) {
      console.error('❌ Login error:', error);
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        throw new Error('Cannot connect to server. Please check if the backend is running.');
      }
      throw error;
    }
  }

  async logout() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await fetch(`${this.baseURL}/auth/logout/`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    }
    
    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    this.token = null;
  }

  async getProfile() {
    const response = await fetch(`${this.baseURL}/auth/profile/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
      method: 'POST',
      headers: this.getHeaders(false),
      body: JSON.stringify({ refresh: refreshToken }),
    });

    const data = await this.handleResponse(response);
    localStorage.setItem('access_token', data.access);
    this.token = data.access;
    return data;
  }

  // Notes APIs
  async getNotes() {
    const response = await fetch(`${this.baseURL}/users/notes/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async createNote(noteData) {
    const response = await fetch(`${this.baseURL}/users/notes/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(noteData),
    });
    return this.handleResponse(response);
  }

  async updateNote(noteId, noteData) {
    const response = await fetch(`${this.baseURL}/users/notes/${noteId}/`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(noteData),
    });
    return this.handleResponse(response);
  }

  async deleteNote(noteId) {
    const response = await fetch(`${this.baseURL}/users/notes/${noteId}/`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    await this.handleResponse(response);
    return { success: true };
  }

  // Progress APIs
  async getProgress() {
    const response = await fetch(`${this.baseURL}/progress/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async updateProgress(progressData) {
    const response = await fetch(`${this.baseURL}/progress/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(progressData),
    });
    return this.handleResponse(response);
  }

  // Assessment APIs
  async getAssessments() {
    const response = await fetch(`${this.baseURL}/assessments/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async generateAssessment(subject, difficulty = 'medium') {
    const response = await fetch(`${this.baseURL}/assessments/generate/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ subject, difficulty }),
    });
    return this.handleResponse(response);
  }

  async submitAssessment(assessmentId, answers) {
    const response = await fetch(`${this.baseURL}/assessments/${assessmentId}/submit/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ answers }),
    });
    return this.handleResponse(response);
  }

  async getAssessmentResults(assessmentId) {
    const response = await fetch(`${this.baseURL}/assessments/${assessmentId}/results/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  // Teacher APIs
  async getStudents() {
    const response = await fetch(`${this.baseURL}/teacher/students/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async getStudentProgress(studentId) {
    const response = await fetch(`${this.baseURL}/teacher/students/${studentId}/progress/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async getClassAnalytics() {
    const response = await fetch(`${this.baseURL}/teacher/analytics/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  // Admin APIs
  async getAllUsers() {
    const response = await fetch(`${this.baseURL}/admin/users/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async getSystemAnalytics() {
    const response = await fetch(`${this.baseURL}/admin/analytics/`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  async manageUser(userId, action, data = {}) {
    const response = await fetch(`${this.baseURL}/admin/users/${userId}/${action}/`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  // Generic API methods
  async get(endpoint, isRetry = false) {
    console.log('🔄 Making GET request to:', `${this.baseURL}${endpoint}`);
    
    if (!isRetry) {
      this.refreshTokenFromStorage();
    }
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      headers: this.getHeaders(),
    });
    
    const result = await this.handleResponse(response, isRetry);
    
    // If token was refreshed, retry the request
    if (result === 'TOKEN_REFRESHED') {
      return this.get(endpoint, true);
    }
    
    return result;
  }

  async post(endpoint, data = {}, options = {}, isRetry = false) {
    console.log('🔄 Making POST request to:', `${this.baseURL}${endpoint}`);
    console.log('🔄 Current token:', this.token ? 'Present' : 'Missing');
    
    if (!isRetry) {
      this.refreshTokenFromStorage();
    }
    
    let headers = this.getHeaders();
    let body;
    
    // Handle FormData - don't set Content-Type, let browser set it with boundary
    if (data instanceof FormData) {
      console.log('🔄 Detected FormData, removing Content-Type header');
      delete headers['Content-Type'];
      body = data;
    } else {
      body = JSON.stringify(data);
    }
    
    // Override headers with any provided in options
    if (options.headers) {
      headers = { ...headers, ...options.headers };
      // Don't override Content-Type if it's FormData
      if (data instanceof FormData && options.headers['Content-Type']) {
        delete headers['Content-Type'];
      }
    }
    
    console.log('🔄 Headers:', headers);
    console.log('🔄 Request data type:', data instanceof FormData ? 'FormData' : 'JSON');
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers,
      body,
    });
    
    const result = await this.handleResponse(response, isRetry);
    
    // If token was refreshed, retry the request
    if (result === 'TOKEN_REFRESHED') {
      return this.post(endpoint, data, options, true);
    }
    
    return result;
  }

  async put(endpoint, data = {}) {
    console.log('🔄 Making PUT request to:', `${this.baseURL}${endpoint}`);
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  async delete(endpoint) {
    console.log('🔄 Making DELETE request to:', `${this.baseURL}${endpoint}`);
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    return this.handleResponse(response);
  }

  // Utility methods
  isAuthenticated() {
    return !!this.token;
  }

  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  getUserRole() {
    const user = this.getUser();
    return user?.role || null;
  }
}

const apiService = new APIService();
export default apiService;
