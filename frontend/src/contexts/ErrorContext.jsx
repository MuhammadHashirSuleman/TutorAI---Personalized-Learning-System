import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { toast } from 'react-toastify';

// Error types
export const ERROR_TYPES = {
  NETWORK: 'NETWORK_ERROR',
  AUTHENTICATION: 'AUTHENTICATION_ERROR',
  AUTHORIZATION: 'AUTHORIZATION_ERROR',
  VALIDATION: 'VALIDATION_ERROR',
  SERVER: 'SERVER_ERROR',
  UNKNOWN: 'UNKNOWN_ERROR'
};

// Error severity levels
export const ERROR_SEVERITY = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
};

const initialState = {
  errors: [],
  networkError: false,
  isOnline: navigator.onLine
};

const errorReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_ERROR':
      return {
        ...state,
        errors: [...state.errors, { ...action.payload, id: Date.now() }]
      };
    
    case 'REMOVE_ERROR':
      return {
        ...state,
        errors: state.errors.filter(error => error.id !== action.payload)
      };
    
    case 'CLEAR_ERRORS':
      return {
        ...state,
        errors: []
      };
    
    case 'SET_NETWORK_ERROR':
      return {
        ...state,
        networkError: action.payload
      };
    
    case 'SET_ONLINE_STATUS':
      return {
        ...state,
        isOnline: action.payload
      };
    
    default:
      return state;
  }
};

const ErrorContext = createContext();

export const useError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
};

export const ErrorProvider = ({ children }) => {
  const [state, dispatch] = useReducer(errorReducer, initialState);

  // Add error handler
  const addError = useCallback((error, type = ERROR_TYPES.UNKNOWN, severity = ERROR_SEVERITY.MEDIUM) => {
    const errorData = {
      message: error.message || error,
      type,
      severity,
      timestamp: new Date().toISOString(),
      stack: error.stack
    };

    dispatch({
      type: 'ADD_ERROR',
      payload: errorData
    });

    // Show toast notification
    const toastOptions = {
      position: 'top-right',
      autoClose: severity === ERROR_SEVERITY.HIGH || severity === ERROR_SEVERITY.CRITICAL ? false : 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true
    };

    switch (severity) {
      case ERROR_SEVERITY.LOW:
        toast.info(errorData.message, toastOptions);
        break;
      case ERROR_SEVERITY.MEDIUM:
        toast.warning(errorData.message, toastOptions);
        break;
      case ERROR_SEVERITY.HIGH:
        toast.error(errorData.message, toastOptions);
        break;
      case ERROR_SEVERITY.CRITICAL:
        toast.error(`Critical Error: ${errorData.message}`, toastOptions);
        break;
      default:
        toast.error(errorData.message, toastOptions);
    }

    return errorData.id;
  }, []);

  // Remove error handler
  const removeError = useCallback((errorId) => {
    dispatch({
      type: 'REMOVE_ERROR',
      payload: errorId
    });
  }, []);

  // Clear all errors
  const clearErrors = useCallback(() => {
    dispatch({ type: 'CLEAR_ERRORS' });
  }, []);

  // Handle API errors
  const handleApiError = useCallback((error, context = '') => {
    let errorType = ERROR_TYPES.UNKNOWN;
    let severity = ERROR_SEVERITY.MEDIUM;
    let message = 'An unexpected error occurred';

    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          errorType = ERROR_TYPES.VALIDATION;
          message = data.message || data.error || 'Invalid request';
          severity = ERROR_SEVERITY.LOW;
          break;
        case 401:
          errorType = ERROR_TYPES.AUTHENTICATION;
          message = 'Authentication required. Please log in.';
          severity = ERROR_SEVERITY.HIGH;
          break;
        case 403:
          errorType = ERROR_TYPES.AUTHORIZATION;
          message = 'You do not have permission to perform this action.';
          severity = ERROR_SEVERITY.MEDIUM;
          break;
        case 404:
          errorType = ERROR_TYPES.VALIDATION;
          message = 'Requested resource not found';
          severity = ERROR_SEVERITY.LOW;
          break;
        case 500:
        case 502:
        case 503:
          errorType = ERROR_TYPES.SERVER;
          message = 'Server error. Please try again later.';
          severity = ERROR_SEVERITY.HIGH;
          break;
        default:
          message = data.message || data.error || `HTTP Error ${status}`;
      }
    } else if (error.request) {
      errorType = ERROR_TYPES.NETWORK;
      message = 'Network error. Please check your connection.';
      severity = ERROR_SEVERITY.HIGH;
      dispatch({ type: 'SET_NETWORK_ERROR', payload: true });
    }

    const fullMessage = context ? `${context}: ${message}` : message;
    return addError({ message: fullMessage }, errorType, severity);
  }, [addError]);

  // Network status handlers
  const handleOnline = useCallback(() => {
    dispatch({ type: 'SET_ONLINE_STATUS', payload: true });
    dispatch({ type: 'SET_NETWORK_ERROR', payload: false });
    toast.success('Connection restored');
  }, []);

  const handleOffline = useCallback(() => {
    dispatch({ type: 'SET_ONLINE_STATUS', payload: false });
    dispatch({ type: 'SET_NETWORK_ERROR', payload: true });
    toast.warning('You are offline. Some features may not work properly.');
  }, []);

  // Set up network event listeners
  React.useEffect(() => {
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [handleOnline, handleOffline]);

  const value = {
    ...state,
    addError,
    removeError,
    clearErrors,
    handleApiError
  };

  return (
    <ErrorContext.Provider value={value}>
      {children}
    </ErrorContext.Provider>
  );
};
