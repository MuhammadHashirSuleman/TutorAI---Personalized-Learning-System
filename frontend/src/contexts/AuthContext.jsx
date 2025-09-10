import React, { createContext, useContext, useState, useEffect } from 'react';
import apiService from '../services/apiService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const login = async (email, password) => {
    setIsLoading(true);
    try {
      const response = await apiService.login({ email, password });
      setUser(response.user);
      return response.user;
    } catch (error) {
      throw new Error(error.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData) => {
    setIsLoading(true);
    try {
      console.log('🔍 Register function called with userData:', userData);
      
      // Validate required fields first
      const requiredFields = ['firstName', 'lastName', 'email', 'password', 'confirmPassword', 'role'];
      const missingFields = requiredFields.filter(field => !userData[field] || userData[field].trim() === '');
      
      if (missingFields.length > 0) {
        throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
      }
      
      // Map frontend field names to backend field names
      const mappedUserData = {
        username: userData.email.trim(), // Use email as username
        email: userData.email.trim(),
        password: userData.password,
        password_confirm: userData.confirmPassword,
        first_name: userData.firstName.trim(),
        last_name: userData.lastName.trim(),
        role: userData.role,
      };
      
      console.log('🔄 Mapped user data for backend:', mappedUserData);
      
      const response = await apiService.register(mappedUserData);
      setUser(response.user);
      return response.user;
    } catch (error) {
      console.error('❌ Registration error in AuthContext:', error);
      throw new Error(error.message || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiService.logout();
    } finally {
      setUser(null);
    }
  };

  // Check for existing user on component mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedUser = apiService.getUser();
        if (storedUser && apiService.isAuthenticated()) {
          // Use stored user data without immediately verifying with server
          // This prevents automatic logout on app load
          setUser(storedUser);
          console.log('✅ Using stored user data:', storedUser.email);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        await apiService.logout();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const value = {
    user,
    login,
    register,
    logout,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
