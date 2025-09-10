import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  Button,
  LinearProgress,
  Chip,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Psychology,
  School,
  Assessment,
  EmojiEvents,
  PlayArrow,
  BookmarkBorder,
  Schedule,
  AutoStories,
  Analytics,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { getRecommendedCourses } from '../data/courses';
import { userApiService } from '../services/userApi';
import { getMyAIClasses, getAIAnalytics } from '../data/classes';
import { DailyQuote } from '../components/features';

const DashboardPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [greeting, setGreeting] = useState('');
  const [userStats, setUserStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');
    
    // Fetch real user stats from database
    fetchUserStats();
  }, []);

  const fetchUserStats = async () => {
    try {
      const stats = await userApiService.getDashboardStats();
      setUserStats(stats);
    } catch (error) {
      console.error('Error fetching user stats:', error);
      // Provide basic fallback data without mock complexity
      setUserStats({
        total_courses: 0,
        completed_courses: 0,
        courses_in_progress: 0,
        average_score: 0,
        profile_completion: 50,
        full_name: `${user?.firstName} ${user?.lastName}` || user?.email || 'User'
      });
    } finally {
      setLoading(false);
    }
  };

  // Real data from database
  const getStats = () => {
    if (!userStats) return [];
    
    if (user?.role === 'student') {
      return [
        {
          title: 'Courses Enrolled',
          value: userStats.total_courses?.toString() || '0',
          change: `${userStats.completed_courses || 0} completed`,
          icon: AutoStories,
          color: '#10b981',
          gradient: 'linear-gradient(135deg, #10b981 0%, #000000 100%)',
        },
        {
          title: 'Average Score',
          value: `${Math.round(userStats.average_score || 0)}%`,
          change: 'Keep improving!',
          icon: EmojiEvents,
          color: '#10b981',
          gradient: 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
        },
        {
          title: 'Profile Complete',
          value: `${userStats.profile_completion || 0}%`,
          change: 'Complete for better recommendations',
          icon: Psychology,
          color: '#10b981',
          gradient: 'linear-gradient(135deg, #000000 0%, #10b981 100%)',
        },
      ];
    } else if (user?.role === 'teacher') {
      return [
        {
          title: 'Total Classes',
          value: userStats.total_classes?.toString() || '0',
          change: `${userStats.active_classes || 0} active`,
          icon: School,
          color: '#10b981',
          gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        },
        {
          title: 'Total Students',
          value: userStats.total_students?.toString() || '0',
          change: 'Across all classes',
          icon: EmojiEvents,
          color: '#10b981',
          gradient: 'linear-gradient(135deg, #34d399 0%, #10b981 100%)',
        },
        {
          title: 'Courses Created',
          value: userStats.total_courses_created?.toString() || '0',
          change: 'Published courses',
          icon: Assessment,
          color: '#10b981',
          gradient: 'linear-gradient(135deg, #10b981 0%, #000000 100%)',
        },
        {
          title: 'Profile Complete',
          value: `${userStats.profile_completion || 0}%`,
          change: 'Update your profile',
          icon: Psychology,
          color: '#10b981',
          gradient: 'linear-gradient(135deg, #000000 0%, #10b981 100%)',
        },
      ];
    }
    return [];
  };
  
  const stats = getStats();

  // Get real courses based on user's field
  const recommendedCourses = getRecommendedCourses(user?.primarySubject || 'computer-science').slice(0, 3);
  
  const recentCourses = recommendedCourses.map((course, index) => ({
    id: course.id,
    title: course.title,
    progress: [65, 45, 85][index] || 50, // Simulate progress
    nextLesson: course.topics[0] || 'Introduction',
    instructor: course.instructor,
    thumbnail: course.thumbnail,
    url: course.url,
    provider: course.provider,
  }));

  const aiRecommendations = [
    {
      type: 'Course',
      title: 'Deep Learning Specialization',
      reason: 'Based on your interest in ML',
      difficulty: 'Intermediate',
    },
    {
      type: 'Assessment',
      title: 'Python Programming Quiz',
      reason: 'Reinforce recent learning',
      difficulty: 'Beginner',
    },
    {
      type: 'Study Plan',
      title: 'Math for Data Science',
      reason: 'Strengthen your foundation',
      difficulty: 'Intermediate',
    },
  ];

  const upcomingEvents = [
    {
      title: 'Live Q&A Session',
      time: '2:00 PM Today',
      type: 'Virtual Event',
    },
    {
      title: 'Assignment Due',
      time: 'Tomorrow',
      type: 'Deadline',
    },
    {
      title: 'Weekly Assessment',
      time: 'Friday',
      type: 'Test',
    },
  ];

  const renderDashboardContent = () => (
    <>
      {/* Welcome Section */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
          {greeting}, {user?.firstName}!
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
          Ready to continue your learning journey?
        </Typography>
        
        {/* AI Insight Alert */}
        <Alert
          severity="info"
          sx={{
            mb: 2,
            background: 'linear-gradient(135deg, rgba(102, 102, 234, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)',
            border: '1px solid rgba(102, 102, 234, 0.2)',
          }}
          icon={<Psychology />}
        >
          <Typography variant="body2">
            <strong>AI Insight:</strong> You learn best in the morning! Your engagement is 40% higher between 9-11 AM.
          </Typography>
        </Alert>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={index}>
            <Card
              sx={{
                height: '100%',
                background: stat.gradient,
                color: 'white',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                },
              }}
            >
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={1.5}>
                  <Avatar
                    sx={{
                      bgcolor: 'rgba(255, 255, 255, 0.2)',
                      width: 56,
                      height: 56,
                    }}
                  >
                    <stat.icon fontSize="large" />
                  </Avatar>
                </Box>
                <Typography variant="h3" fontWeight="bold" gutterBottom>
                  {stat.value}
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9, mb: 1 }}>
                  {stat.title}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.8 }}>
                  {stat.change}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Continue Learning */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                Continue Learning
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Pick up where you left off
              </Typography>
              
              {recentCourses.map((course, index) => (
                <Paper
                  key={course.id}
                  sx={{
                    p: 2,
                    mb: index === recentCourses.length - 1 ? 0 : 1.5,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    transition: 'all 0.2s',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: theme => theme.shadows[4],
                    },
                  }}
                >
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={8}>
                      <Box display="flex" alignItems="center" mb={1.5}>
                        <Avatar
                          sx={{
                            mr: 1.5,
                            width: 40,
                            height: 40,
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          }}
                        >
                          <AutoStories />
                        </Avatar>
                        <Box flexGrow={1}>
                          <Typography variant="h6" fontWeight="600">
                            {course.title}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            by {course.instructor} • Next: {course.nextLesson}
                          </Typography>
                        </Box>
                      </Box>
                      <Box display="flex" alignItems="center" mb={1}>
                        <Typography variant="body2" sx={{ mr: 1 }}>
                          Progress: {course.progress}%
                        </Typography>
                        <Box sx={{ flexGrow: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={course.progress}
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                        </Box>
                      </Box>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Box display="flex" gap={1} justifyContent={{ xs: 'stretch', md: 'flex-end' }} flexDirection={{ xs: 'column', sm: 'row', md: 'row' }}>
                        <IconButton color="primary">
                          <BookmarkBorder />
                        </IconButton>
                        <Button
                          variant="contained"
                          startIcon={<PlayArrow />}
                          onClick={() => window.open(course.url, '_blank')}
                        >
                          Start Learning
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </Paper>
              ))}
            </CardContent>
          </Card>

          {/* AI Recommendations */}
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                AI Recommendations
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Personalized suggestions based on your learning pattern
              </Typography>
              
              <Grid container spacing={2}>
                {aiRecommendations.map((rec, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Paper
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        border: '1px solid rgba(102, 102, 234, 0.2)',
                        background: 'linear-gradient(135deg, rgba(102, 102, 234, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%)',
                      }}
                    >
                      <Box display="flex" alignItems="center" mb={1}>
                        <Chip
                          label={rec.type}
                          size="small"
                          color="primary"
                          sx={{ mr: 1 }}
                        />
                        <Chip
                          label={rec.difficulty}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                      <Typography variant="subtitle1" fontWeight="600" mb={1}>
                        {rec.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {rec.reason}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Sidebar */}
        <Grid item xs={12} lg={4} sx={{ order: { xs: -1, lg: 0 } }}>
          {/* Quick Actions */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 2 }}>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection={{ xs: 'row', lg: 'column' }} gap={1.5} sx={{ flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<Psychology />}
                  fullWidth
                  sx={{ flex: { xs: 1, lg: 'none' } }}
                  onClick={() => navigate('/chatbot')}
                >
                  Ask AI Tutor
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Analytics />}
                  fullWidth
                  sx={{ flex: { xs: 1, lg: 'none' } }}
                  onClick={() => navigate('/progress')}
                >
                  View Analytics
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Daily Quote Widget */}
          <Box sx={{ mb: 2 }}>
            <DailyQuote />
          </Box>

          {/* Upcoming Events */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600, mb: 1.5 }}>
                Upcoming Events
              </Typography>
              <List dense disablePadding>
                {upcomingEvents.map((event, index) => (
                  <ListItem key={index} sx={{ px: 0, py: 1 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                        <Schedule fontSize="small" />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={event.title}
                      secondary={`${event.time} • ${event.type}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          {/* Learning Streak */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                Learning Streak
              </Typography>
              <Typography variant="h3" color="primary" fontWeight="bold" gutterBottom>
                15 Days
              </Typography>
              <Typography variant="body2" color="text.secondary" mb={2}>
                You're on fire! Keep learning every day to maintain your streak.
              </Typography>
              <LinearProgress
                variant="determinate"
                value={75}
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="caption" color="text.secondary">
                75% to next milestone (30 days)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, p: { xs: 1, sm: 2, md: 3 }, maxWidth: '100%', overflow: 'hidden' }}>
      {/* Header with user info */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 700 }}>
          {greeting}, {userStats?.full_name || user?.firstName}!
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
          {user?.role === 'student' 
            ? 'Ready to continue your learning journey?' 
            : 'Welcome to your teaching dashboard!'}
        </Typography>
      </Box>

      {/* Dashboard Content */}
      {renderDashboardContent()}
    </Box>
  );
};

export default DashboardPage;
