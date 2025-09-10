import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  IconButton,
  Badge,
  Popover,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
  Button,
  CircularProgress,
  Tooltip,
  Avatar,
} from '@mui/material';
import {
  Notifications,
  NotificationsActive,
  School,
  Assignment,
  PersonAdd,
  Info,
  CheckCircle,
  Clear,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { useAuth } from '../../contexts/AuthContext';
import { userApiService } from '../../services/userApi';

const NotificationDropdown = () => {
  const theme = useTheme();
  const { user } = useAuth();
  const [anchorEl, setAnchorEl] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef(null);

  const isOpen = Boolean(anchorEl);

  // Notification type configurations
  const notificationTypes = {
    enrollment_request: {
      icon: PersonAdd,
      color: '#2196f3',
      label: 'Enrollment Request'
    },
    assignment_created: {
      icon: Assignment,
      color: '#ff9800',
      label: 'New Assignment'
    },
    student_joined: {
      icon: School,
      color: '#4caf50',
      label: 'Student Joined'
    },
    system_message: {
      icon: Info,
      color: '#9c27b0',
      label: 'System Message'
    },
    announcement: {
      icon: NotificationsActive,
      color: '#ff5722',
      label: 'Announcement'
    }
  };

  // Priority colors
  const priorityColors = {
    low: '#9e9e9e',
    medium: '#ff9800',
    high: '#f44336',
    urgent: '#d32f2f'
  };

  // Fetch notifications
  const fetchNotifications = async () => {
    if (!user) return;
    
    try {
      const data = await userApiService.getNotifications();
      setNotifications(data.notifications || []);
      setStats({ 
        unread_count: data.unread_count || 0,
        urgent_count: (data.notifications || []).filter(n => n.priority === 'urgent' && !n.is_read).length
      });
    } catch (error) {
      console.error('Error fetching notifications:', error);
      // Fallback to empty state
      setNotifications([]);
      setStats({ unread_count: 0, urgent_count: 0 });
    }
  };

  // Fetch notification stats
  const fetchStats = async () => {
    if (!user) return;
    
    try {
      const data = await userApiService.getNotifications();
      setStats({ 
        unread_count: data.unread_count || 0,
        urgent_count: (data.notifications || []).filter(n => n.priority === 'urgent' && !n.is_read).length
      });
    } catch (error) {
      console.error('Error fetching notification stats:', error);
      setStats({ unread_count: 0, urgent_count: 0 });
    }
  };

  // Mark notification as read
  const markAsRead = async (notificationId) => {
    if (!user) return;
    
    try {
      await userApiService.markNotificationRead(notificationId);
      fetchNotifications();
      fetchStats();
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    if (!user) return;
    
    try {
      // Mark all notifications as read by fetching with mark_read=true
      await userApiService.getNotifications(true);
      fetchNotifications();
      fetchStats();
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  // Delete notification (not implemented in backend yet)
  const deleteNotification = async (notificationId) => {
    if (!user) return;
    
    try {
      // This functionality would need to be added to the backend
      console.warn('Delete notification functionality not yet implemented');
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  // Handle notification click
  const handleNotificationClick = (event) => {
    setAnchorEl(event.currentTarget);
    if (!isOpen) {
      setLoading(true);
      fetchNotifications().finally(() => setLoading(false));
    }
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  // Format time ago
  const formatTimeAgo = (dateString) => {
    if (!dateString) return 'Just now';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    
    return date.toLocaleDateString();
  };

  // Get notification icon
  const getNotificationIcon = (type) => {
    const config = notificationTypes[type] || notificationTypes.system_message;
    const IconComponent = config.icon;
    return <IconComponent sx={{ color: config.color, fontSize: 20 }} />;
  };

  // Get priority chip
  const getPriorityChip = (priority) => {
    if (!priority || priority === 'low') return null;
    
    return (
      <Chip
        label={priority.toUpperCase()}
        size="small"
        sx={{
          backgroundColor: priorityColors[priority],
          color: 'white',
          fontSize: '0.7rem',
          height: 20,
          '& .MuiChip-label': {
            px: 1,
          },
        }}
      />
    );
  };

  // Initialize and cleanup
  useEffect(() => {
    if (user) {
      fetchStats();
      // Poll for updates every 30 seconds
      intervalRef.current = setInterval(fetchStats, 30000);
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [user]);


  return (
    <>
      <Tooltip title={`Notifications (${stats.unread_count || 0} unread)`}>
        <IconButton
          color="inherit"
          onClick={handleNotificationClick}
          sx={{
            color: '#10b981',
          }}
        >
          <Badge 
            badgeContent={stats.unread_count || 0} 
            color="error"
            max={99}
          >
            {stats.urgent_count > 0 ? (
              <NotificationsActive sx={{ 
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': {
                    transform: 'scale(1)',
                  },
                  '50%': {
                    transform: 'scale(1.1)',
                  },
                  '100%': {
                    transform: 'scale(1)',
                  },
                }
              }} />
            ) : (
              <Notifications />
            )}
          </Badge>
        </IconButton>
      </Tooltip>

      <Popover
        anchorEl={anchorEl}
        open={isOpen}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: {
            width: 400,
            maxHeight: 600,
            mt: 1,
            boxShadow: theme.shadows[8],
          },
        }}
      >
        <Paper>
          {/* Header */}
          <Box
            sx={{
              p: 2,
              borderBottom: `1px solid ${theme.palette.divider}`,
              backgroundColor: theme.palette.primary.main,
              color: 'white',
            }}
          >
            <Typography variant="h6" fontWeight="bold">
              Notifications
            </Typography>
            
            {stats.unread_count > 0 && (
              <Typography variant="body2" sx={{ opacity: 0.9, mt: 0.5 }}>
                {stats.unread_count} unread notification{stats.unread_count !== 1 ? 's' : ''}
                {stats.urgent_count > 0 && ` • ${stats.urgent_count} urgent`}
              </Typography>
            )}
          </Box>


          {/* Notifications List */}
          <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
            {loading ? (
              <Box display="flex" justifyContent="center" p={3}>
                <CircularProgress size={24} />
              </Box>
            ) : notifications.length === 0 ? (
              <Box textAlign="center" py={4}>
                <Notifications sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  No notifications yet
                </Typography>
              </Box>
            ) : (
              <List disablePadding>
                {notifications.map((notification, index) => (
                  <React.Fragment key={notification.id}>
                    <ListItem
                      sx={{
                        px: 2,
                        py: 1.5,
                        cursor: 'pointer',
                        backgroundColor: notification.is_read 
                          ? 'transparent' 
                          : 'action.hover',
                        '&:hover': {
                          backgroundColor: 'action.selected',
                        },
                      }}
                      onClick={() => !notification.is_read && markAsRead(notification.id)}
                    >
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        {getNotificationIcon(notification.type)}
                      </ListItemIcon>
                      
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" justifyContent="space-between">
                            <Typography
                              variant="subtitle2"
                              sx={{
                                fontWeight: notification.is_read ? 'normal' : 'bold',
                                flex: 1,
                              }}
                            >
                              {notification.title}
                            </Typography>
                            {getPriorityChip(notification.priority)}
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                              }}
                            >
                              {notification.message}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                              {formatTimeAgo(notification.created_at)}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                    {index < notifications.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Box>

          {/* Footer Actions */}
          {notifications.length > 0 && (
            <Box
              sx={{
                p: 2,
                borderTop: `1px solid ${theme.palette.divider}`,
                textAlign: 'center',
              }}
            >
              <Button
                variant="text"
                size="small"
                onClick={markAllAsRead}
                disabled={stats.unread_count === 0}
              >
                Mark All as Read
              </Button>
            </Box>
          )}
        </Paper>
      </Popover>

    </>
  );
};

export default NotificationDropdown;
