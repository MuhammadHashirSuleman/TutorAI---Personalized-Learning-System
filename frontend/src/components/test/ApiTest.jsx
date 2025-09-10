import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Grid,
} from '@mui/material';
import { userApiService } from '../../services/userApi';

const ApiTest = () => {
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const testApiConnection = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Test basic API connectivity
      console.log('Testing API connection...');
      
      // Test profile endpoint
      const profileData = await userApiService.getCurrentUserProfile();
      setProfile(profileData);
      console.log('Profile data:', profileData);

      // Test dashboard stats endpoint
      const statsData = await userApiService.getDashboardStats();
      setStats(statsData);
      console.log('Stats data:', statsData);

      setSuccess(true);
    } catch (error) {
      console.error('API Test Error:', error);
      setError(error.message || 'API connection failed');
    } finally {
      setLoading(false);
    }
  };

  const testUserSearch = async () => {
    try {
      setLoading(true);
      const searchResults = await userApiService.searchUsers('test', { limit: 5 });
      console.log('Search results:', searchResults);
      alert(`Found ${searchResults.length} users`);
    } catch (error) {
      console.error('Search test error:', error);
      setError('User search failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        API Integration Test
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Test API Connection
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              onClick={testApiConnection}
              disabled={loading}
              sx={{ mr: 2 }}
            >
              {loading ? <CircularProgress size={20} /> : 'Test Profile & Stats API'}
            </Button>
            
            <Button
              variant="outlined"
              onClick={testUserSearch}
              disabled={loading}
            >
              Test User Search
            </Button>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              API connection successful! Check console for detailed data.
            </Alert>
          )}
        </CardContent>
      </Card>

      {profile && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Profile Data
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Email
                </Typography>
                <Typography variant="body1">{profile.email}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Role
                </Typography>
                <Chip 
                  label={profile.role?.toUpperCase()} 
                  color={profile.role === 'admin' ? 'error' : 'primary'}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Full Name
                </Typography>
                <Typography variant="body1">
                  {profile.first_name && profile.last_name 
                    ? `${profile.first_name} ${profile.last_name}`
                    : profile.username || 'Not set'
                  }
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Verified
                </Typography>
                <Chip 
                  label={profile.is_verified ? 'VERIFIED' : 'NOT VERIFIED'}
                  color={profile.is_verified ? 'success' : 'default'}
                  size="small"
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {stats && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Dashboard Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  Profile Completion
                </Typography>
                <Typography variant="h4" color="primary">
                  {stats.profile_completion || 0}%
                </Typography>
              </Grid>
              
              {stats.total_courses !== undefined && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Courses
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {stats.total_courses}
                  </Typography>
                </Grid>
              )}

              {stats.total_classes !== undefined && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Classes
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {stats.total_classes}
                  </Typography>
                </Grid>
              )}

              {stats.average_score !== undefined && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">
                    Average Score
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {Math.round(stats.average_score)}%
                  </Typography>
                </Grid>
              )}
            </Grid>

            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Raw Data (check console for full details)
              </Typography>
              <Box
                component="pre"
                sx={{
                  p: 1,
                  bgcolor: 'grey.100',
                  borderRadius: 1,
                  fontSize: '0.75rem',
                  overflow: 'auto',
                  maxHeight: 200,
                }}
              >
                {JSON.stringify(stats, null, 2)}
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ApiTest;
