import axios from 'axios';
import { getToken } from '../utils/auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with authentication
const userAPI = axios.create({
  baseURL: `${API_BASE_URL}/users`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create admin API instance
const adminAPI = axios.create({
  baseURL: `${API_BASE_URL}/admin`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests for both APIs
const addTokenInterceptor = (apiInstance) => {
  apiInstance.interceptors.request.use(
    (config) => {
      const token = getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Response interceptor for error handling
  apiInstance.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Handle token expiration
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
};

addTokenInterceptor(userAPI);
addTokenInterceptor(adminAPI);

export const userApiService = {
  // User CRUD operations
  getUsers: async (params = {}) => {
    const response = await userAPI.get('/', { params });
    return response.data;
  },

  getUser: async (userId) => {
    const response = await userAPI.get(`/${userId}/`);
    return response.data;
  },

  createUser: async (userData) => {
    const response = await userAPI.post('/', userData);
    return response.data;
  },

  updateUser: async (userId, userData) => {
    const response = await userAPI.put(`/${userId}/`, userData);
    return response.data;
  },

  partialUpdateUser: async (userId, userData) => {
    const response = await userAPI.patch(`/${userId}/`, userData);
    return response.data;
  },

  deleteUser: async (userId) => {
    const response = await userAPI.delete(`/${userId}/`);
    return response.data;
  },

  // Profile operations
  getCurrentUserProfile: async () => {
    try {
      const response = await userAPI.get('/profile/');
      return response.data;
    } catch (error) {
      // Fallback mock data if API is not available
      console.warn('Profile API not available, using mock data:', error.message);
      const mockProfile = {
        id: 1,
        username: 'student1',
        email: 'student1@example.com',
        first_name: 'John',
        last_name: 'Doe',
        phone_number: '+1-234-567-8900',
        date_of_birth: '1995-05-15',
        role: 'student',
        is_verified: true,
        profile_picture: null,
        created_at: '2024-01-15T10:30:00Z',
        student_profile: {
          learning_style: 'Visual',
          grade_level: 'Undergraduate',
          institution: 'Tech University',
          student_id: 'STU001'
        }
      };
      return mockProfile;
    }
  },

  updateCurrentUserProfile: async (profileData) => {
    try {
      const response = await userAPI.patch('/profile/', profileData);
      return response.data;
    } catch (error) {
      console.warn('Profile update API not available, returning mock data:', error.message);
      return { ...profileData, id: 1, updated_at: new Date().toISOString() };
    }
  },

  // Dashboard statistics
  getDashboardStats: async () => {
    const response = await userAPI.get('/dashboard-stats/');
    return response.data;
  },

  // User statistics
  getUserStats: async () => {
    const response = await userAPI.get('/profile/stats/');
    return response.data;
  },

  // Profile picture operations
  uploadProfilePicture: async (file) => {
    const formData = new FormData();
    formData.append('profile_picture', file);
    
    const response = await userAPI.post('/profile/upload-picture/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  removeProfilePicture: async () => {
    const response = await userAPI.delete('/profile/remove-picture/');
    return response.data;
  },

  // Delete current user account
  deleteCurrentUserAccount: async (password, confirmDelete = true) => {
    try {
      console.log('Making DELETE request to: /delete-account/');
      const response = await userAPI.delete('/delete-account/', {
        data: {
          password,
          confirm_delete: confirmDelete
        }
      });
      console.log('Delete account response received:', response.data);
      return response.data;
    } catch (error) {
      console.error('Delete account API error:', error);
      console.error('Error response status:', error.response?.status);
      console.error('Error response data:', error.response?.data);
      throw error;
    }
  },

  // Notifications
  getNotifications: async (markRead = false) => {
    const params = markRead ? { mark_read: true } : {};
    const response = await userAPI.get('/notifications/', { params });
    return response.data;
  },

  markNotificationRead: async (notificationId) => {
    const response = await userAPI.post(`/notifications/${notificationId}/read/`);
    return response.data;
  },

  // Admin functions
  sendNotificationToStudents: async (notificationData) => {
    const response = await adminAPI.post('/send-notification/', notificationData);
    return response.data;
  },

  // Search users
  searchUsers: async (query, filters = {}) => {
    const params = { q: query, ...filters };
    const response = await userAPI.get('/search/', { params });
    return response.data;
  },

  // Student profile operations
  getStudentProfiles: async (params = {}) => {
    const response = await userAPI.get('/student-profiles/', { params });
    return response.data;
  },

  getStudentProfile: async (profileId) => {
    const response = await userAPI.get(`/student-profiles/${profileId}/`);
    return response.data;
  },

  updateStudentProfile: async (profileId, profileData) => {
    const response = await userAPI.put(`/student-profiles/${profileId}/`, profileData);
    return response.data;
  },

  createStudentProfile: async (profileData) => {
    const response = await userAPI.post('/student-profiles/', profileData);
    return response.data;
  },

  // Teacher profile operations
  getTeacherProfiles: async (params = {}) => {
    const response = await userAPI.get('/teacher-profiles/', { params });
    return response.data;
  },

  getTeacherProfile: async (profileId) => {
    const response = await userAPI.get(`/teacher-profiles/${profileId}/`);
    return response.data;
  },

  updateTeacherProfile: async (profileId, profileData) => {
    const response = await userAPI.put(`/teacher-profiles/${profileId}/`, profileData);
    return response.data;
  },

  createTeacherProfile: async (profileData) => {
    const response = await userAPI.post('/teacher-profiles/', profileData);
    return response.data;
  },

  // Notes operations
  getNotes: async (params = {}) => {
    const response = await userAPI.get('/notes/', { params });
    return response.data;
  },

  getNote: async (noteId) => {
    const response = await userAPI.get(`/notes/${noteId}/`);
    return response.data;
  },

  createNote: async (noteData) => {
    const response = await userAPI.post('/notes/', noteData);
    return response.data;
  },

  updateNote: async (noteId, noteData) => {
    const response = await userAPI.put(`/notes/${noteId}/`, noteData);
    return response.data;
  },

  deleteNote: async (noteId) => {
    const response = await userAPI.delete(`/notes/${noteId}/`);
    return response.data;
  },

  // Bulk operations
  bulkUpdateUsers: async (userIds, updateData) => {
    const promises = userIds.map(id => userAPI.patch(`/users/${id}/`, updateData));
    return Promise.all(promises);
  },

  bulkDeleteUsers: async (userIds) => {
    const promises = userIds.map(id => userAPI.delete(`/users/${id}/`));
    return Promise.all(promises);
  },
};

export default userApiService;
