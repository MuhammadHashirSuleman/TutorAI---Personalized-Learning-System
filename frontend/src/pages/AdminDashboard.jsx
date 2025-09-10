import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Avatar,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Alert,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  SupervisorAccount,
  School,
  Assessment,
  Analytics,
  TrendingUp,
  Person,
  Group,
  Block,
  CheckCircle,
  Edit,
  Delete,
  Add,
  Search,
  Psychology,
  Computer,
  Storage,
  Security,
  Settings,
  Notifications,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/apiService';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState([]);
  const [systemAnalytics, setSystemAnalytics] = useState({});
  const [selectedUser, setSelectedUser] = useState(null);
  const [userDialogOpen, setUserDialogOpen] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  // Check if user is admin
  const isAdmin = user?.role === 'admin';

  // Ensure data is fetched only for admins, but keep hook unconditionally called
  useEffect(() => {
    if (isAdmin) {
      fetchData();
    } else {
      // Non-admins shouldn't stay in loading state
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin]);


  const fetchData = async () => {
    try {
      setLoading(true);
      setError(''); // Clear any previous errors
      
      // Fetch data with better error handling
      const [usersData, analyticsData] = await Promise.all([
        apiService.getAllUsers().catch(err => {
          console.error('Failed to fetch users:', err);
          throw new Error('Failed to fetch users: ' + err.message);
        }),
        apiService.getSystemAnalytics().catch(err => {
          console.error('Failed to fetch analytics:', err);
          throw new Error('Failed to fetch system analytics: ' + err.message);
        })
      ]);
      
      // Set the fetched data
      setUsers(usersData.results || usersData || []);
      setSystemAnalytics(analyticsData || {});
      
      console.log('Admin data fetched successfully:', {
        userCount: usersData.results?.length || usersData?.length || 0,
        analyticsKeys: Object.keys(analyticsData || {})
      });
      
    } catch (error) {
      console.error('Failed to fetch admin data:', error);
      setError(`Failed to load admin dashboard: ${error.message}`);
      // Set empty defaults on error
      setUsers([]);
      setSystemAnalytics({});
    } finally {
      setLoading(false);
    }
  };

  const handleUserAction = async (userId, action, data = {}) => {
    try {
      setActionLoading(true);
      setError('');
      
      console.log(`Performing ${action} on user ${userId}`, data);
      
      await apiService.manageUser(userId, action, data);
      
      // Show success message
      console.log(`Successfully ${action}ed user`);
      
      // Refresh data to show changes
      await fetchData();
      
      // Close dialog if it was open
      if (userDialogOpen) {
        setUserDialogOpen(false);
        setSelectedUser(null);
      }
      
    } catch (error) {
      console.error(`Failed to ${action} user:`, error);
      setError(`Failed to ${action} user: ${error.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.first_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.last_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFilter = filterRole === 'all' || user.role === filterRole;
    
    return matchesSearch && matchesFilter;
  });

  // Always use real data from API - no mock fallbacks
  const displayUsers = filteredUsers;
  const displayAnalytics = systemAnalytics;

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <SupervisorAccount />;
      case 'teacher':
        return <School />;
      default:
        return <Person />;
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'teacher':
        return 'warning';
      default:
        return 'primary';
    }
  };

  if (loading) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Container maxWidth="xl">
          <Typography variant="h4" gutterBottom>Loading admin dashboard...</Typography>
        </Container>
      </Box>
    );
  }

  // After hooks are called: if not admin, show access denied
  if (!isAdmin) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Container maxWidth="xl">
          <Alert severity="error" sx={{ mb: 3 }}>
            <Typography variant="h6">Access Denied</Typography>
            <Typography variant="body2">
              You must be an administrator to access this dashboard.
            </Typography>
          </Alert>
        </Container>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Container maxWidth="xl">
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
            Administrator Dashboard
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Manage users, monitor system performance, and oversee platform operations
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* System Overview Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} lg={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
                    <Group fontSize="large" />
                  </Avatar>
                </Box>
                <Typography variant="h3" fontWeight="bold" gutterBottom>
                  {displayAnalytics.total_users || 0}
                </Typography>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  Total Users
                </Typography>
                <Typography variant="body2" color="success.main">
                  {displayAnalytics.active_users || 0} active
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} lg={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Avatar sx={{ bgcolor: 'success.main', width: 56, height: 56 }}>
                    <School fontSize="large" />
                  </Avatar>
                </Box>
                <Typography variant="h3" fontWeight="bold" gutterBottom>
                  {displayAnalytics.courses_created || 0}
                </Typography>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  Courses Created
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Platform wide
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} lg={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Avatar sx={{ bgcolor: 'warning.main', width: 56, height: 56 }}>
                    <Psychology fontSize="large" />
                  </Avatar>
                </Box>
                <Typography variant="h3" fontWeight="bold" gutterBottom>
                  {((displayAnalytics.ai_interactions || 0) / 1000).toFixed(1)}K
                </Typography>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  AI Interactions
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total interactions
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} lg={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                  <Avatar sx={{ bgcolor: 'info.main', width: 56, height: 56 }}>
                    <TrendingUp fontSize="large" />
                  </Avatar>
                </Box>
                <Typography variant="h3" fontWeight="bold" gutterBottom>
                  {displayAnalytics.system_uptime || 0}%
                </Typography>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  System Uptime
                </Typography>
                <Typography variant="body2" color="success.main">
                  Excellent
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs */}
        <Box sx={{ mb: 3 }}>
          <Tabs value={currentTab} onChange={(e, newValue) => setCurrentTab(newValue)}>
            <Tab label="User Management" />
            <Tab label="System Analytics" />
            <Tab label="Platform Settings" />
            <Tab label="Security & Logs" />
          </Tabs>
        </Box>

        {/* User Management Tab */}
        {currentTab === 0 && (
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5" fontWeight="bold">
                  User Management
                </Typography>
                <Box display="flex" gap={2}>
                  <TextField
                    size="small"
                    placeholder="Search users..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Search />
                        </InputAdornment>
                      ),
                    }}
                  />
                  <FormControl size="small" sx={{ minWidth: 120 }}>
                    <InputLabel>Role</InputLabel>
                    <Select
                      value={filterRole}
                      onChange={(e) => setFilterRole(e.target.value)}
                      label="Role"
                    >
                      <MenuItem value="all">All Roles</MenuItem>
                      <MenuItem value="student">Students</MenuItem>
                      <MenuItem value="teacher">Teachers</MenuItem>
                      <MenuItem value="admin">Administrators</MenuItem>
                    </Select>
                  </FormControl>
                  <Button variant="contained" startIcon={<Add />}>
                    Add User
                  </Button>
                </Box>
              </Box>

              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>User</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Last Login</TableCell>
                      <TableCell>Join Date</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {displayUsers.map((userData) => (
                      <TableRow key={userData.id}>
                        <TableCell>
                          <Box display="flex" alignItems="center">
                            <Avatar sx={{ mr: 2 }}>
                              {getRoleIcon(userData.role)}
                            </Avatar>
                            <Box>
                              <Typography variant="subtitle2" fontWeight="bold">
                                {userData.first_name} {userData.last_name}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {userData.email}
                              </Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={userData.role}
                            color={getRoleColor(userData.role)}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={userData.is_active ? 'Active' : 'Inactive'}
                            color={userData.is_active ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {userData.last_login ? new Date(userData.last_login).toLocaleDateString() : 'Never'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(userData.date_joined).toLocaleDateString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <IconButton
                            onClick={() => {
                              setSelectedUser(userData);
                              setUserDialogOpen(true);
                            }}
                            color="primary"
                          >
                            <Edit />
                          </IconButton>
                          <IconButton
                            onClick={() => handleUserAction(userData.id, userData.is_active ? 'deactivate' : 'activate')}
                            color={userData.is_active ? 'error' : 'success'}
                            disabled={actionLoading}
                          >
                            {userData.is_active ? <Block /> : <CheckCircle />}
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}

        {/* System Analytics Tab */}
        {currentTab === 1 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    User Role Distribution
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Students</Typography>
                      <Typography variant="body2">{displayAnalytics.total_students || 0}</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={displayAnalytics.total_users ? ((displayAnalytics.total_students || 0) / displayAnalytics.total_users) * 100 : 0}
                      sx={{ mb: 2, height: 8, borderRadius: 4 }}
                    />
                    
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Teachers</Typography>
                      <Typography variant="body2">{displayAnalytics.total_teachers || 0}</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={displayAnalytics.total_users ? ((displayAnalytics.total_teachers || 0) / displayAnalytics.total_users) * 100 : 0}
                      color="warning"
                      sx={{ mb: 2, height: 8, borderRadius: 4 }}
                    />
                    
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Administrators</Typography>
                      <Typography variant="body2">{displayAnalytics.total_admins || 0}</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={displayAnalytics.total_users ? ((displayAnalytics.total_admins || 0) / displayAnalytics.total_users) * 100 : 0}
                      color="error"
                      sx={{ mb: 2, height: 8, borderRadius: 4 }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    System Resources
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Box display="flex" justifyContent="space-between" mb={2}>
                      <Typography>Storage Used:</Typography>
                      <Typography fontWeight="bold">{displayAnalytics.storage_used || 0}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={displayAnalytics.storage_used || 0}
                      color={(displayAnalytics.storage_used || 0) > 80 ? 'error' : 'primary'}
                      sx={{ mb: 3, height: 8, borderRadius: 4 }}
                    />
                    
                    <Box display="flex" justifyContent="space-between" mb={2}>
                      <Typography>API Calls Today:</Typography>
                      <Typography fontWeight="bold">{(displayAnalytics.api_calls_today || 0).toLocaleString()}</Typography>
                    </Box>
                    
                    <Box display="flex" justifyContent="space-between" mb={2}>
                      <Typography>System Uptime:</Typography>
                      <Typography fontWeight="bold" color="success.main">
                        {displayAnalytics.system_uptime || 0}%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Platform Settings Tab */}
        {currentTab === 2 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    General Settings
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Allow new user registrations"
                    />
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Enable AI tutor for all users"
                    />
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Enable email notifications"
                    />
                    <FormControlLabel
                      control={<Switch />}
                      label="Maintenance mode"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    AI Configuration
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <TextField
                      fullWidth
                      label="Max AI interactions per day"
                      defaultValue="100"
                      type="number"
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      label="AI response timeout (seconds)"
                      defaultValue="30"
                      type="number"
                      sx={{ mb: 2 }}
                    />
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Enable AI conversation logging"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Security & Logs Tab */}
        {currentTab === 3 && (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Security & System Logs
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Alert severity="info" sx={{ mb: 2 }}>
                  System security monitoring is active. No suspicious activities detected.
                </Alert>
                
                <Typography variant="subtitle2" gutterBottom>
                  Recent Security Events
                </Typography>
                
                <Box sx={{ mt: 2 }}>
                  {[
                    { type: 'login', user: 'jane.smith@example.com', time: '2024-01-16 14:30', status: 'success' },
                    { type: 'failed_login', user: 'unknown@example.com', time: '2024-01-16 13:45', status: 'blocked' },
                    { type: 'password_change', user: 'john.doe@example.com', time: '2024-01-16 12:20', status: 'success' },
                  ].map((event, index) => (
                    <Box key={index} display="flex" alignItems="center" py={1} borderBottom="1px solid #eee">
                      <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                        <Security fontSize="small" />
                      </Avatar>
                      <Box flexGrow={1}>
                        <Typography variant="body2">
                          {event.type.replace('_', ' ').toUpperCase()}: {event.user}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {event.time}
                        </Typography>
                      </Box>
                      <Chip
                        label={event.status}
                        color={event.status === 'success' ? 'success' : 'error'}
                        size="small"
                      />
                    </Box>
                  ))}
                </Box>
              </Box>
            </CardContent>
          </Card>
        )}

        {/* User Edit Dialog */}
        <Dialog
          open={userDialogOpen}
          onClose={() => setUserDialogOpen(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>
            Edit User: {selectedUser?.first_name} {selectedUser?.last_name}
          </DialogTitle>
          <DialogContent>
            {selectedUser && (
              <Box sx={{ pt: 2 }}>
                <TextField
                  fullWidth
                  label="First Name"
                  defaultValue={selectedUser.first_name}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Last Name"
                  defaultValue={selectedUser.last_name}
                  sx={{ mb: 2 }}
                />
                <TextField
                  fullWidth
                  label="Email"
                  defaultValue={selectedUser.email}
                  sx={{ mb: 2 }}
                />
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Role</InputLabel>
                  <Select defaultValue={selectedUser.role} label="Role">
                    <MenuItem value="student">Student</MenuItem>
                    <MenuItem value="teacher">Teacher</MenuItem>
                    <MenuItem value="admin">Administrator</MenuItem>
                  </Select>
                </FormControl>
                <FormControlLabel
                  control={<Switch defaultChecked={selectedUser.is_active} />}
                  label="Active Account"
                />
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setUserDialogOpen(false)}>Cancel</Button>
            <Button 
              variant="contained" 
              onClick={() => handleUserAction(selectedUser?.id, 'update', selectedUser)}
            >
              Save Changes
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default AdminDashboard;
