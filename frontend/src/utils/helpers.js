/**
 * Helper utility functions for the AI Study platform
 */

/**
 * Format a date string or Date object to a human-readable format
 * @param {string|Date} date - The date to format
 * @returns {string} Formatted date string
 */
export const formatDate = (date) => {
  if (!date) return '';
  
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  const now = new Date();
  const diffInMs = now - dateObj;
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
  
  if (diffInDays === 0) {
    return 'Today';
  } else if (diffInDays === 1) {
    return 'Yesterday';
  } else if (diffInDays < 7) {
    return `${diffInDays} days ago`;
  } else if (diffInDays < 30) {
    const weeks = Math.floor(diffInDays / 7);
    return weeks === 1 ? '1 week ago' : `${weeks} weeks ago`;
  } else if (diffInDays < 365) {
    const months = Math.floor(diffInDays / 30);
    return months === 1 ? '1 month ago' : `${months} months ago`;
  } else {
    const years = Math.floor(diffInDays / 365);
    return years === 1 ? '1 year ago' : `${years} years ago`;
  }
};

/**
 * Format file size in bytes to human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
export const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B';
  
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`;
};

/**
 * Format duration in seconds to human-readable format
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
export const formatDuration = (seconds) => {
  if (!seconds || seconds === 0) return '0s';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${remainingSeconds}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    return `${remainingSeconds}s`;
  }
};

/**
 * Truncate text to a specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Capitalize first letter of each word
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
export const capitalizeWords = (str) => {
  if (!str) return '';
  return str.replace(/\w\S*/g, (txt) => 
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  );
};

/**
 * Generate a random color for UI elements
 * @returns {string} Hex color code
 */
export const getRandomColor = () => {
  const colors = [
    '#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2',
    '#5e35b1', '#1976d2', '#0288d1', '#00796b', '#689f38',
    '#f57c00', '#ff5722', '#e91e63', '#9c27b0', '#673ab7'
  ];
  return colors[Math.floor(Math.random() * colors.length)];
};

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} Whether email is valid
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Debounce function to limit how often a function can be called
 * @param {function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {function} Debounced function
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Get file icon based on file extension
 * @param {string} filename - Name of the file
 * @returns {string} Material-UI icon name
 */
export const getFileIcon = (filename) => {
  if (!filename) return 'InsertDriveFile';
  
  const ext = filename.toLowerCase().split('.').pop();
  
  switch (ext) {
    case 'pdf':
      return 'PictureAsPdf';
    case 'doc':
    case 'docx':
      return 'Description';
    case 'xls':
    case 'xlsx':
      return 'TableChart';
    case 'ppt':
    case 'pptx':
      return 'Slideshow';
    case 'txt':
      return 'TextSnippet';
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
      return 'Image';
    case 'mp4':
    case 'avi':
    case 'mov':
      return 'VideoFile';
    case 'mp3':
    case 'wav':
      return 'AudioFile';
    case 'zip':
    case 'rar':
      return 'Archive';
    default:
      return 'InsertDriveFile';
  }
};

/**
 * Get appropriate status color for different states
 * @param {string} status - Status string
 * @returns {string} Material-UI color
 */
export const getStatusColor = (status) => {
  switch (status?.toLowerCase()) {
    case 'completed':
    case 'success':
    case 'active':
      return 'success';
    case 'processing':
    case 'pending':
    case 'in-progress':
      return 'warning';
    case 'failed':
    case 'error':
    case 'cancelled':
      return 'error';
    case 'paused':
    case 'inactive':
      return 'default';
    default:
      return 'default';
  }
};

/**
 * Format number with thousand separators
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export const formatNumber = (num) => {
  if (typeof num !== 'number') return '0';
  return num.toLocaleString();
};

/**
 * Calculate reading time for text
 * @param {string} text - Text to calculate reading time for
 * @param {number} wordsPerMinute - Average words per minute (default: 200)
 * @returns {string} Estimated reading time
 */
export const calculateReadingTime = (text, wordsPerMinute = 200) => {
  if (!text) return '0 min';
  
  const wordCount = text.split(/\s+/).length;
  const readingTimeMinutes = Math.ceil(wordCount / wordsPerMinute);
  
  if (readingTimeMinutes < 1) {
    return '< 1 min';
  } else if (readingTimeMinutes === 1) {
    return '1 min';
  } else {
    return `${readingTimeMinutes} min`;
  }
};

/**
 * Deep clone an object
 * @param {any} obj - Object to clone
 * @returns {any} Cloned object
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  
  const cloned = {};
  for (let key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloned[key] = deepClone(obj[key]);
    }
  }
  return cloned;
};

/**
 * Check if user is on mobile device
 * @returns {boolean} Whether user is on mobile
 */
export const isMobile = () => {
  return window.innerWidth < 768;
};

/**
 * Scroll to element smoothly
 * @param {string} elementId - ID of element to scroll to
 */
export const scrollToElement = (elementId) => {
  const element = document.getElementById(elementId);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' });
  }
};
