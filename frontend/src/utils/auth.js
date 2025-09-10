// Authentication utility functions

/**
 * Get authentication token from localStorage
 * @returns {string|null} JWT token or null if not found
 */
export const getToken = () => {
  try {
    return localStorage.getItem('token') || localStorage.getItem('access_token');
  } catch (error) {
    console.error('Error getting token from localStorage:', error);
    return null;
  }
};

/**
 * Set authentication token in localStorage
 * @param {string} token - JWT token to store
 */
export const setToken = (token) => {
  try {
    localStorage.setItem('token', token);
  } catch (error) {
    console.error('Error setting token in localStorage:', error);
  }
};

/**
 * Remove authentication token from localStorage
 */
export const removeToken = () => {
  try {
    localStorage.removeItem('token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  } catch (error) {
    console.error('Error removing token from localStorage:', error);
  }
};

/**
 * Get refresh token from localStorage
 * @returns {string|null} Refresh token or null if not found
 */
export const getRefreshToken = () => {
  try {
    return localStorage.getItem('refresh_token');
  } catch (error) {
    console.error('Error getting refresh token from localStorage:', error);
    return null;
  }
};

/**
 * Set refresh token in localStorage
 * @param {string} refreshToken - Refresh token to store
 */
export const setRefreshToken = (refreshToken) => {
  try {
    localStorage.setItem('refresh_token', refreshToken);
  } catch (error) {
    console.error('Error setting refresh token in localStorage:', error);
  }
};

/**
 * Check if user is authenticated (has valid token)
 * @returns {boolean} True if authenticated, false otherwise
 */
export const isAuthenticated = () => {
  const token = getToken();
  if (!token) return false;

  try {
    // Basic token validation - check if it's not expired
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    
    // Check if token is expired
    if (payload.exp < currentTime) {
      removeToken(); // Remove expired token
      return false;
    }
    
    return true;
  } catch (error) {
    // If token is malformed, consider user as not authenticated
    console.error('Invalid token format:', error);
    removeToken();
    return false;
  }
};

/**
 * Get user information from token
 * @returns {object|null} User data or null if not available
 */
export const getUserFromToken = () => {
  const token = getToken();
  if (!token) return null;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      id: payload.user_id,
      email: payload.email,
      role: payload.role,
      exp: payload.exp,
      iat: payload.iat,
    };
  } catch (error) {
    console.error('Error parsing token:', error);
    return null;
  }
};

/**
 * Set authentication data (both access and refresh tokens)
 * @param {object} authData - Object containing access and refresh tokens
 * @param {string} authData.access - Access token
 * @param {string} authData.refresh - Refresh token
 */
export const setAuthData = (authData) => {
  try {
    if (authData.access || authData.access_token) {
      setToken(authData.access || authData.access_token);
    }
    if (authData.refresh || authData.refresh_token) {
      setRefreshToken(authData.refresh || authData.refresh_token);
    }
  } catch (error) {
    console.error('Error setting auth data:', error);
  }
};

/**
 * Clear all authentication data
 */
export const clearAuthData = () => {
  removeToken();
};

/**
 * Get authorization headers for API requests
 * @returns {object} Headers object with Authorization header
 */
export const getAuthHeaders = () => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Check if token is about to expire (within 5 minutes)
 * @returns {boolean} True if token expires soon, false otherwise
 */
export const isTokenExpiringSoon = () => {
  const token = getToken();
  if (!token) return false;

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    const timeUntilExpiry = payload.exp - currentTime;
    
    // Return true if token expires within 5 minutes (300 seconds)
    return timeUntilExpiry < 300;
  } catch (error) {
    console.error('Error checking token expiry:', error);
    return false;
  }
};

/**
 * Format user role for display
 * @param {string} role - User role from token/API
 * @returns {string} Formatted role name
 */
export const formatRole = (role) => {
  switch (role?.toLowerCase()) {
    case 'student':
      return 'Student';
    case 'teacher':
      return 'Teacher';
    case 'admin':
      return 'Administrator';
    default:
      return role || 'User';
  }
};

const authUtils = {
  getToken,
  setToken,
  removeToken,
  getRefreshToken,
  setRefreshToken,
  isAuthenticated,
  getUserFromToken,
  setAuthData,
  clearAuthData,
  getAuthHeaders,
  isTokenExpiringSoon,
  formatRole,
};

export default authUtils;
