import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  Button,
  Grid,
  TextField,
  Divider,
  Chip,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import {
  Edit,
  PhotoCamera,
  School,
  Email,
  Phone,
  CalendarToday,
  Person,
  Work,
  LocationOn,
  Star,
  TrendingUp,
  BookmarkBorder,
  Timeline,
  Close,
  DeleteForever,
} from '@mui/icons-material';
import { userApiService } from '../../services/userApi';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

// Utility function for date formatting
const formatDate = (dateString, formatType = 'full') => {
  if (!dateString) return '';
  const date = new Date(dateString);
  
  if (formatType === 'full') {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
  
  if (formatType === 'monthYear') {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long'
    });
  }
  
  return date.toLocaleDateString();
};

const MyProfile = () => {
  const { user: authUser, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState({});
  const [uploading, setUploading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [deletePassword, setDeletePassword] = useState('');
  const [deleting, setDeleting] = useState(false);
  
  useEffect(() => {
    fetchProfileData();
  }, []);
  
  // Ensure delete confirmation is always reset when dialog is closed
  useEffect(() => {
    if (!deleteDialogOpen) {
      setDeleteConfirmation('');
      setDeletePassword('');
    }
  }, [deleteDialogOpen]);

  const fetchProfileData = async () => {
    setLoading(true);
    try {
      const [profileData, statsData] = await Promise.all([
        userApiService.getCurrentUserProfile(),
        userApiService.getDashboardStats()
      ]);
      
      setProfile(profileData);
      setStats(statsData);
      setEditData({
        first_name: profileData.first_name || '',
        last_name: profileData.last_name || '',
        phone_number: profileData.phone_number || '',
        date_of_birth: profileData.date_of_birth || '',
      });
    } catch (error) {
      console.error('Error fetching profile data:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load profile data',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleProfilePictureUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const response = await userApiService.uploadProfilePicture(file);
      setProfile(prev => ({
        ...prev,
        profile_picture: response.profile_picture_url
      }));
      setSnackbar({
        open: true,
        message: 'Profile picture updated successfully!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error uploading profile picture:', error);
      setSnackbar({
        open: true,
        message: 'Failed to update profile picture',
        severity: 'error'
      });
    } finally {
      setUploading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      const updatedProfile = await userApiService.updateCurrentUserProfile(editData);
      setProfile(updatedProfile);
      setEditMode(false);
      setSnackbar({
        open: true,
        message: 'Profile updated successfully!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error updating profile:', error);
      setSnackbar({
        open: true,
        message: 'Failed to update profile',
        severity: 'error'
      });
    }
  };

  const handleDeleteAccount = async () => {
    console.log('Delete button clicked!');
    console.log('Delete confirmation value:', deleteConfirmation);
    console.log('Delete password length:', deletePassword?.length);
    
    if (deleteConfirmation !== 'DELETE MY ACCOUNT') {
      setSnackbar({
        open: true,
        message: 'Please type "DELETE MY ACCOUNT" to confirm',
        severity: 'error'
      });
      return;
    }

    if (!deletePassword) {
      setSnackbar({
        open: true,
        message: 'Please enter your password to confirm deletion',
        severity: 'error'
      });
      return;
    }

    setDeleting(true);
    try {
      console.log('Attempting to delete account...');
      console.log('Current user:', authUser);
      console.log('Authentication token exists:', !!localStorage.getItem('token'));
      
      const result = await userApiService.deleteCurrentUserAccount(deletePassword, true);
      console.log('Delete account response:', result);
      
      setSnackbar({
        open: true,
        message: 'Account deleted successfully. Redirecting...',
        severity: 'success'
      });
      
      // Close the dialog
      setDeleteDialogOpen(false);
      setDeleteConfirmation('');
      setDeletePassword('');
      
      // Logout user and clear auth state
      setTimeout(async () => {
        try {
          await logout();
        } catch (logoutError) {
          console.warn('Logout after delete failed:', logoutError);
        }
        navigate('/login');
      }, 2000);
    } catch (error) {
      console.error('=== DELETE ACCOUNT ERROR DETAILS ===');
      console.error('Full error object:', error);
      console.error('Error name:', error.name);
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
      
      if (error.response) {
        console.error('Response status:', error.response.status);
        console.error('Response statusText:', error.response.statusText);
        console.error('Response headers:', error.response.headers);
        console.error('Response data:', error.response.data);
        console.error('Response config:', error.response.config);
      } else if (error.request) {
        console.error('Request made but no response:', error.request);
      }
      console.error('===============================');
      
      let errorMessage = 'Failed to delete account';
      
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message && error.message !== 'Network Error') {
        errorMessage = `Failed to delete account: ${error.message}`;
      } else if (error.response?.status === 404) {
        errorMessage = 'Delete account endpoint not found. Please contact support.';
      } else if (error.response?.status === 403) {
        errorMessage = 'You do not have permission to delete this account.';
      } else if (error.response?.status === 401) {
        errorMessage = 'You must be logged in to delete your account.';
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error occurred while deleting account. Please try again later.';
      } else if (error.name === 'NetworkError' || error.message === 'Network Error') {
        errorMessage = 'Network error. Please check your connection and try again.';
      }
      
      setSnackbar({
        open: true,
        message: errorMessage,
        severity: 'error'
      });
    } finally {
      setDeleting(false);
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'student': return '#2196f3';
      case 'teacher': return '#4caf50';
      case 'admin': return '#ff9800';
      default: return '#757575';
    }
  };

  const getCompletionColor = (percentage) => {
    if (percentage >= 80) return '#4caf50';
    if (percentage >= 60) return '#ff9800';
    return '#f44336';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (!profile) {
    return (
      <Alert severity="error">
        Failed to load profile data. Please try refreshing the page.
      </Alert>
    );
  }

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      {/* Profile Header */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item>
              <Box position="relative">
                <Avatar
                  src={profile.profile_picture}
                  alt={profile.first_name || profile.username}
                  sx={{
                    width: 120,
                    height: 120,
                    fontSize: '2rem',
                    bgcolor: getRoleColor(profile.role),
                  }}
                >
                  {!profile.profile_picture && 
                    (profile.first_name?.[0] || profile.username?.[0] || 'U')
                  }
                </Avatar>
                <IconButton
                  component="label"
                  disabled={uploading}
                  sx={{
                    position: 'absolute',
                    bottom: -8,
                    right: -8,
                    bgcolor: 'primary.main',
                    color: 'white',
                    '&:hover': { bgcolor: 'primary.dark' },
                  }}
                >
                  <PhotoCamera />
                  <input
                    hidden
                    accept="image/*"
                    type="file"
                    onChange={handleProfilePictureUpload}
                  />
                </IconButton>
                {uploading && (
                  <CircularProgress
                    size={24}
                    sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      marginTop: '-12px',
                      marginLeft: '-12px',
                    }}
                  />
                )}
              </Box>
            </Grid>
            
            <Grid item xs>
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                {profile.first_name && profile.last_name 
                  ? `${profile.first_name} ${profile.last_name}`
                  : profile.username
                }
              </Typography>
              
              <Box display="flex" alignItems="center" gap={1} mb={2}>
                <Chip
                  label={profile.role?.toUpperCase()}
                  size="small"
                  sx={{
                    bgcolor: getRoleColor(profile.role),
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                />
                {profile.is_verified && (
                  <Chip
                    label="VERIFIED"
                    size="small"
                    color="success"
                    icon={<Star />}
                  />
                )}
              </Box>

              <Typography color="text.secondary" gutterBottom>
                <Email fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                {profile.email}
              </Typography>

              {profile.phone_number && (
                <Typography color="text.secondary" gutterBottom>
                  <Phone fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                  {profile.phone_number}
                </Typography>
              )}

              {profile.date_of_birth && (
                <Typography color="text.secondary" gutterBottom>
                  <CalendarToday fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Born {formatDate(profile.date_of_birth, 'full')}
                </Typography>
              )}

              <Typography color="text.secondary">
                Member since {formatDate(profile.created_at, 'monthYear')}
              </Typography>
            </Grid>

            <Grid item>
              <Box display="flex" gap={2}>
                <Button
                  variant="contained"
                  startIcon={<Edit />}
                  onClick={() => setEditMode(true)}
                >
                  Edit Profile
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteForever />}
                  onClick={() => {
                    console.log('Delete Account button clicked - resetting state');
                    setDeleteConfirmation('');
                    setDeletePassword('');
                    setDeleteDialogOpen(true);
                  }}
                >
                  Delete Account
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Profile Completion */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Profile Completion
              </Typography>
              <Box sx={{ mb: 2 }}>
                <LinearProgress
                  variant="determinate"
                  value={stats?.profile_completion || 0}
                  sx={{
                    height: 10,
                    borderRadius: 5,
                    '& .MuiLinearProgress-bar': {
                      bgcolor: getCompletionColor(stats?.profile_completion || 0),
                    },
                  }}
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                {stats?.profile_completion || 0}% completed
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Complete your profile to get better recommendations
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Role-Specific Stats */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {profile.role === 'student' ? 'Academic Progress' : 'Teaching Stats'}
              </Typography>
              
              {profile.role === 'student' && stats && (
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="primary" fontWeight="bold">
                        {stats.total_courses || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Courses
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="success.main" fontWeight="bold">
                        {stats.completed_courses || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Completed
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="warning.main" fontWeight="bold">
                        {Math.round(stats.average_score || 0)}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Avg Score
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="info.main" fontWeight="bold">
                        {Math.round((stats.study_time || 0) / 60)}h
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Study Time
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              )}

              {profile.role === 'teacher' && stats && (
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="primary" fontWeight="bold">
                        {stats.total_classes || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Classes
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="success.main" fontWeight="bold">
                        {stats.total_students || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Students
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="warning.main" fontWeight="bold">
                        {stats.total_courses_created || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Courses
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="info.main" fontWeight="bold">
                        {stats.active_classes || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Active
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Role-Specific Profile */}
        {(profile.student_profile || profile.teacher_profile) && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {profile.role === 'student' ? 'Student Information' : 'Teaching Information'}
                </Typography>
                
                {profile.student_profile && (
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Learning Style
                      </Typography>
                      <Typography variant="body1">
                        {profile.student_profile.learning_style || 'Not specified'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Grade Level
                      </Typography>
                      <Typography variant="body1">
                        {profile.student_profile.grade_level || 'Not specified'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Institution
                      </Typography>
                      <Typography variant="body1">
                        {profile.student_profile.institution || 'Not specified'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Student ID
                      </Typography>
                      <Typography variant="body1">
                        {profile.student_profile.student_id || 'Not provided'}
                      </Typography>
                    </Grid>
                  </Grid>
                )}

                {profile.teacher_profile && (
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Department
                      </Typography>
                      <Typography variant="body1">
                        {profile.teacher_profile.department || 'Not specified'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Specialization
                      </Typography>
                      <Typography variant="body1">
                        {profile.teacher_profile.specialization || 'Not specified'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Institution
                      </Typography>
                      <Typography variant="body1">
                        {profile.teacher_profile.institution || 'Not specified'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Experience
                      </Typography>
                      <Typography variant="body1">
                        {profile.teacher_profile.experience_years ? 
                          `${profile.teacher_profile.experience_years} years` : 
                          'Not specified'
                        }
                      </Typography>
                    </Grid>
                    {profile.teacher_profile.bio && (
                      <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          Bio
                        </Typography>
                        <Typography variant="body1">
                          {profile.teacher_profile.bio}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Edit Profile Dialog */}
      <Dialog open={editMode} onClose={() => setEditMode(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Edit Profile
          <IconButton
            sx={{ position: 'absolute', right: 8, top: 8 }}
            onClick={() => setEditMode(false)}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="First Name"
                value={editData.first_name}
                onChange={(e) => setEditData({ ...editData, first_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Last Name"
                value={editData.last_name}
                onChange={(e) => setEditData({ ...editData, last_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Phone Number"
                value={editData.phone_number}
                onChange={(e) => setEditData({ ...editData, phone_number: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Date of Birth"
                type="date"
                value={editData.date_of_birth}
                onChange={(e) => setEditData({ ...editData, date_of_birth: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditMode(false)}>Cancel</Button>
          <Button onClick={handleSaveProfile} variant="contained">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Account Confirmation Dialog */}
      <Dialog 
        key={deleteDialogOpen ? 'open' : 'closed'}
        open={deleteDialogOpen} 
        onClose={() => {
          setDeleteDialogOpen(false);
          setDeleteConfirmation('');
          setDeletePassword('');
        }}
        onEntering={() => {
          // Reset fields when dialog opens
          console.log('Dialog entering - clearing fields');
          setDeleteConfirmation('');
          setDeletePassword('');
          // Force clear after a short delay to override autofill
          setTimeout(() => {
            console.log('Delayed clear - ensuring fields are empty');
            setDeleteConfirmation('');
            setDeletePassword('');
          }, 100);
        }}
        maxWidth="sm" 
        fullWidth
      >
        <DialogTitle sx={{ color: 'error.main' }}>
          <Box display="flex" alignItems="center" gap={1}>
            <DeleteForever color="error" />
            Delete Account
          </Box>
          <IconButton
            sx={{ position: 'absolute', right: 8, top: 8 }}
            onClick={() => {
              setDeleteDialogOpen(false);
              setDeleteConfirmation('');
              setDeletePassword('');
            }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Alert severity="error" sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              ⚠️ WARNING: This action cannot be undone!
            </Typography>
            <Typography variant="body2">
              Deleting your account will:
            </Typography>
            <Box component="ul" sx={{ mt: 1, mb: 2 }}>
              <li>Permanently remove all your personal data</li>
              <li>Delete all your courses and progress</li>
              <li>Remove all your notes and saved content</li>
              <li>Cancel any active subscriptions</li>
            </Box>
          </Alert>
          
          <Typography variant="body1" gutterBottom>
            To confirm account deletion, please type <strong>"DELETE MY ACCOUNT"</strong> below:
          </Typography>
          
          <TextField
            fullWidth
            label="Type DELETE MY ACCOUNT"
            name="delete-confirmation-text"
            id="delete-confirmation-field"
            value={deleteConfirmation === 'hashmughal01@gmail.com' ? '' : deleteConfirmation}
            onChange={(e) => {
              const newValue = e.target.value;
              console.log('Confirmation field changed to:', newValue);
              // Prevent email from being set
              if (newValue !== 'hashmughal01@gmail.com' && !newValue.includes('@')) {
                setDeleteConfirmation(newValue);
              } else {
                console.log('Blocking email input, clearing field');
                setDeleteConfirmation('');
              }
            }}
            onFocus={() => {
              console.log('Confirmation field focused, current value:', deleteConfirmation);
              if (deleteConfirmation === 'hashmughal01@gmail.com' || deleteConfirmation.includes('@')) {
                console.log('Clearing email from confirmation field');
                setDeleteConfirmation('');
              }
            }}
            placeholder="DELETE MY ACCOUNT"
            sx={{ mt: 2 }}
            error={deleteConfirmation && deleteConfirmation !== 'DELETE MY ACCOUNT'}
            helperText={deleteConfirmation && deleteConfirmation !== 'DELETE MY ACCOUNT' ? 
              'Please type exactly: DELETE MY ACCOUNT' : ''
            }
            autoComplete="one-time-code"
            autoCorrect="off"
            spellCheck={false}
            inputProps={{
              'data-testid': 'delete-confirmation-input',
              'autoComplete': 'one-time-code',
              'data-lpignore': 'true',
              'data-form-type': 'other',
              'data-1p-ignore': 'true',
              'data-bwignore': 'true'
            }}
            InputProps={{
              autoComplete: 'one-time-code'
            }}
          />
          
          <TextField
            fullWidth
            label="Password"
            type="password"
            value={deletePassword}
            onChange={(e) => setDeletePassword(e.target.value)}
            placeholder="Enter your password"
            sx={{ mt: 2 }}
            required
          />
          
          {/* Debug Info */}
          <Box sx={{ mt: 2, p: 1, bgcolor: 'grey.100', borderRadius: 1, fontSize: '0.75rem' }}>
            <strong>Debug Info:</strong><br/>
            Confirmation: "{deleteConfirmation}"<br/>
            Password Length: {deletePassword?.length || 0}<br/>
            Exact Match: {deleteConfirmation === 'DELETE MY ACCOUNT' ? 'YES' : 'NO'}<br/>
            Button Enabled: {(!deleting && deleteConfirmation === 'DELETE MY ACCOUNT' && !!deletePassword) ? 'YES' : 'NO'}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => {
              setDeleteDialogOpen(false);
              setDeleteConfirmation('');
              setDeletePassword('');
            }}
            disabled={deleting}
          >
            Cancel
          </Button>
          <Button 
            onClick={() => {
              console.log('=== DELETE BUTTON CLICKED ===');
              console.log('deleting:', deleting);
              console.log('deleteConfirmation:', `"${deleteConfirmation}"`);
              console.log('deletePassword length:', deletePassword?.length);
              console.log('Confirmation exact match:', deleteConfirmation === 'DELETE MY ACCOUNT');
              console.log('Button should be enabled:', !deleting && deleteConfirmation === 'DELETE MY ACCOUNT' && !!deletePassword);
              handleDeleteAccount();
            }}
            variant="contained"
            color="error"
            disabled={deleting || deleteConfirmation !== 'DELETE MY ACCOUNT' || !deletePassword}
            startIcon={deleting ? <CircularProgress size={16} /> : <DeleteForever />}
          >
            {deleting ? 'Deleting...' : 'Delete Account'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        message={snackbar.message}
      />
    </Box>
  );
};

export default MyProfile;
