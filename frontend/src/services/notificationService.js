import apiService from './apiService';

class NotificationService {
  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL;
  }

  // Get the appropriate endpoint based on user role
  getEndpoint(userRole, path = '') {
    const rolePrefix = userRole === 'teacher' ? '/api/teacher' : '/api/student';
    return `${rolePrefix}/notifications/${path}`;
  }

  // Get notifications with filtering
  async getNotifications(userRole, filters = {}) {
    try {
      const params = new URLSearchParams();
      
      if (filters.is_read !== undefined) {
        params.append('is_read', filters.is_read.toString());
      }
      
      if (filters.type) {
        params.append('type', filters.type);
      }
      
      if (filters.priority) {
        params.append('priority', filters.priority);
      }
      
      if (filters.limit) {
        params.append('limit', filters.limit.toString());
      }

      const endpoint = this.getEndpoint(userRole);
      const url = params.toString() ? `${endpoint}?${params}` : endpoint;
      
      const response = await apiService.get(url);
      return response.data;
    } catch (error) {
      console.error('Error fetching notifications:', error);
      throw error;
    }
  }

  // Get notification statistics
  async getNotificationStats(userRole) {
    try {
      const endpoint = this.getEndpoint(userRole, 'stats/');
      const response = await apiService.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('Error fetching notification stats:', error);
      throw error;
    }
  }

  // Get specific notification details
  async getNotificationDetail(userRole, notificationId) {
    try {
      const endpoint = this.getEndpoint(userRole, `${notificationId}/`);
      const response = await apiService.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('Error fetching notification detail:', error);
      throw error;
    }
  }

  // Mark specific notifications as read
  async markAsRead(userRole, notificationIds) {
    try {
      const endpoint = this.getEndpoint(userRole);
      const response = await apiService.post(endpoint, {
        notification_ids: Array.isArray(notificationIds) ? notificationIds : [notificationIds]
      });
      return response.data;
    } catch (error) {
      console.error('Error marking notifications as read:', error);
      throw error;
    }
  }

  // Mark all notifications as read
  async markAllAsRead(userRole) {
    try {
      const endpoint = this.getEndpoint(userRole);
      const response = await apiService.put(endpoint, {
        action: 'mark_all_read'
      });
      return response.data;
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      throw error;
    }
  }

  // Delete read notifications
  async deleteReadNotifications(userRole) {
    try {
      const endpoint = this.getEndpoint(userRole);
      const response = await apiService.put(endpoint, {
        action: 'delete_read'
      });
      return response.data;
    } catch (error) {
      console.error('Error deleting read notifications:', error);
      throw error;
    }
  }

  // Update specific notification
  async updateNotification(userRole, notificationId, data) {
    try {
      const endpoint = this.getEndpoint(userRole, `${notificationId}/`);
      const response = await apiService.put(endpoint, data);
      return response.data;
    } catch (error) {
      console.error('Error updating notification:', error);
      throw error;
    }
  }

  // Delete specific notification
  async deleteNotification(userRole, notificationId) {
    try {
      const endpoint = this.getEndpoint(userRole, `${notificationId}/`);
      const response = await apiService.delete(endpoint);
      return response.data;
    } catch (error) {
      console.error('Error deleting notification:', error);
      throw error;
    }
  }

  // Mark notification as read/unread
  async toggleReadStatus(userRole, notificationId, isRead) {
    try {
      return await this.updateNotification(userRole, notificationId, {
        is_read: isRead
      });
    } catch (error) {
      console.error('Error toggling notification read status:', error);
      throw error;
    }
  }

  // Batch operations
  async batchMarkAsRead(userRole, notificationIds) {
    try {
      const promises = notificationIds.map(id => 
        this.updateNotification(userRole, id, { is_read: true })
      );
      const results = await Promise.all(promises);
      return results;
    } catch (error) {
      console.error('Error in batch mark as read:', error);
      throw error;
    }
  }

  // Batch delete
  async batchDelete(userRole, notificationIds) {
    try {
      const promises = notificationIds.map(id => 
        this.deleteNotification(userRole, id)
      );
      const results = await Promise.all(promises);
      return results;
    } catch (error) {
      console.error('Error in batch delete:', error);
      throw error;
    }
  }

  // Get notification type configurations for UI
  getNotificationTypeConfig(type) {
    const configs = {
      enrollment_request: {
        icon: 'PersonAdd',
        color: '#2196f3',
        label: 'Enrollment Request'
      },
      enrollment_approved: {
        icon: 'CheckCircle',
        color: '#4caf50',
        label: 'Enrollment Approved'
      },
      assignment_created: {
        icon: 'Assignment',
        color: '#ff9800',
        label: 'New Assignment'
      },
      assignment_due_soon: {
        icon: 'Schedule',
        color: '#f44336',
        label: 'Assignment Due Soon'
      },
      student_joined: {
        icon: 'School',
        color: '#4caf50',
        label: 'Student Joined'
      },
      class_message: {
        icon: 'Message',
        color: '#2196f3',
        label: 'Class Message'
      },
      system_message: {
        icon: 'Info',
        color: '#9c27b0',
        label: 'System Message'
      }
    };

    return configs[type] || configs.system_message;
  }

  // Get priority color
  getPriorityColor(priority) {
    const colors = {
      low: '#9e9e9e',
      medium: '#ff9800',
      high: '#f44336',
      urgent: '#d32f2f'
    };

    return colors[priority] || colors.low;
  }

  // Format notification time
  formatNotificationTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString();
  }

  // Create notification (for admin/system use)
  async createNotification(recipientId, data) {
    try {
      // This would typically be called from admin panel or system processes
      const response = await apiService.post('/admin/notifications/', {
        recipient: recipientId,
        ...data
      });
      return response.data;
    } catch (error) {
      console.error('Error creating notification:', error);
      throw error;
    }
  }
}

// Create and export singleton instance
const notificationService = new NotificationService();
export default notificationService;
