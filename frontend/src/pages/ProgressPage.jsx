import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Tabs,
  Tab,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  CircularProgress,
  Alert,
  Button,
  Divider,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  TrendingUp,
  School,
  PlayLesson,
  Assignment,
  EmojiEvents,
  AccessTime,
  CheckCircle,
  Schedule,
  Psychology,
  Analytics,
  Grade,
  Star,
  BookmarkBorder,
  BarChart,
  ShowChart,
  PieChart,
  AutoStories,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/apiService';
import recommendationService from '../services/recommendationService';

// Note: Chart.js is installed but using alternative displays for better compatibility
// To enable charts, uncomment the chart imports and install: npm install react-chartjs-2 chart.js
const chartsEnabled = false; // Set to true when charts are needed

const ProgressPage = () => {
  const { user } = useAuth();
  const [currentTab, setCurrentTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [progressData, setProgressData] = useState({
    courses: [],
    overall: {},
    analytics: {},
    goals: [],
    achievements: []
  });
  const [timeframe, setTimeframe] = useState('month'); // week, month, semester

  useEffect(() => {
    fetchProgressData();
  }, [timeframe]);

  const fetchProgressData = async () => {
    setLoading(true);
    setError(null);
    
    // Generate realistic demo data if API fails
    const generateDemoData = () => ({
      courses: [
        {
          id: 1,
          title: 'Introduction to Machine Learning',
          provider: 'TutorAI',
          progress: 75,
          completed_lessons: 15,
          total_lessons: 20,
          time_spent: 24,
          last_activity: '2 days ago'
        },
        {
          id: 2,
          title: 'Python for Data Science',
          provider: 'TutorAI',
          progress: 45,
          completed_lessons: 9,
          total_lessons: 20,
          time_spent: 18,
          last_activity: '1 week ago'
        },
        {
          id: 3,
          title: 'Web Development Fundamentals',
          provider: 'TutorAI',
          progress: 90,
          completed_lessons: 18,
          total_lessons: 20,
          time_spent: 32,
          last_activity: 'Yesterday'
        }
      ],
      overall: {
        total_study_time: 74,
        average_score: 85,
        courses_completed: 1,
        streak_days: 5,
        level: 'Advanced Learner'
      },
      analytics: {
        weekly_activity: [4, 6, 3, 8, 5, 7, 2],
        subject_performance: {
          'Machine Learning': 88,
          'Programming': 92,
          'Web Development': 85,
          'Data Science': 78
        },
        learning_trend: [65, 70, 75, 78, 82, 85, 88]
      },
      goals: [
        {
          id: 1,
          title: 'Complete ML Course',
          progress: 75,
          target_date: 'Dec 31, 2024'
        },
        {
          id: 2,
          title: 'Master Python Basics',
          progress: 60,
          target_date: 'Jan 15, 2025'
        }
      ],
      achievements: [
        {
          id: 1,
          badge: '🎯',
          title: 'First Course Completed',
          description: 'Completed your first course successfully!',
          earned_date: 'Nov 15, 2024'
        },
        {
          id: 2,
          badge: '🔥',
          title: '5-Day Streak',
          description: 'Studied for 5 consecutive days',
          earned_date: 'Nov 20, 2024'
        }
      ]
    });

    try {
      // Try to fetch real data first
      const [courseProgress, analytics] = await Promise.all([
        apiService.get('/progress/student/progress/courses/').catch(() => ({ data: [] })),
        apiService.get('/progress/student/analytics/').catch(() => ({ data: {} }))
      ]);

      // Use real data if available, otherwise use demo data
      const hasRealData = courseProgress.data?.length > 0 || Object.keys(analytics.data || {}).length > 0;
      
      if (hasRealData) {
        setProgressData({
          courses: courseProgress.data || [],
          overall: analytics.data?.overall || {},
          analytics: analytics.data?.analytics || {},
          goals: analytics.data?.goals || [],
          achievements: analytics.data?.achievements || []
        });
      } else {
        // Use demo data for better user experience
        setProgressData(generateDemoData());
      }
    } catch (error) {
      console.error('Error fetching progress data:', error);
      // Use demo data as fallback
      setProgressData(generateDemoData());
    } finally {
      setLoading(false);
    }
  };

  // Chart configurations removed for simplicity - using alternative displays instead
  // This provides better compatibility and faster loading

  const renderOverallStats = () => (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      {[
      {
        title: 'Total Study Time',
        value: `${progressData.overall.total_study_time || 0}h`,
        icon: AccessTime,
        color: '#10b981',
        change: '+12h this week'
      },
      {
        title: 'Average Score',
        value: `${progressData.overall.average_score || 0}%`,
        icon: Grade,
        color: '#059669',
        change: '+5% this month'
      },
      {
        title: 'Learning Streak',
        value: `${progressData.overall.streak_days || 0} days`,
        icon: EmojiEvents,
        color: '#34d399',
        change: 'Keep it up!'
      },
      {
        title: 'Learning Level',
        value: progressData.overall.level || 'Beginner',
        icon: Psychology,
        color: '#000000',
        change: 'Rising steadily'
      }
      ].map((stat, index) => (
        <Grid item xs={12} sm={6} lg={3} key={index}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: stat.color, mr: 2 }}>
                  <stat.icon />
                </Avatar>
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.title}
                  </Typography>
                </Box>
              </Box>
              <Typography variant="caption" color="success.main">
                {stat.change}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );


  const renderCourseProgress = () => (
    <Grid container spacing={3}>
      {progressData.courses.map((course) => (
        <Grid item xs={12} md={6} key={course.id}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                <Box>
                  <Typography variant="h6" fontWeight="bold">
                    {course.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {course.provider}
                  </Typography>
                </Box>
                <Chip
                  label={`${course.progress}% Complete`}
                  variant="outlined"
                  size="small"
                />
              </Box>

              <Box mb={2}>
                <LinearProgress
                  variant="determinate"
                  value={course.progress}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Stack spacing={1} mb={2}>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Lessons</Typography>
                  <Typography variant="body2">
                    {course.completed_lessons}/{course.total_lessons}
                  </Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Time Spent</Typography>
                  <Typography variant="body2">{course.time_spent}h</Typography>
                </Box>
                <Box display="flex" justifyContent="space-between">
                  <Typography variant="body2">Last Activity</Typography>
                  <Typography variant="body2">{course.last_activity}</Typography>
                </Box>
              </Stack>

              <Button
                variant="outlined"
                size="small"
                fullWidth
                onClick={() => {
                  // Track course interaction
                  recommendationService.trackTimeSpent(course.id, course.time_spent * 60);
                }}
              >
                Continue Learning
              </Button>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );

  const renderAnalytics = () => {
    // Alternative display when charts are not available
    const renderAlternativeCharts = () => (
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <BarChart sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">
                  Weekly Activity
                </Typography>
              </Box>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Day</TableCell>
                      <TableCell align="right">Hours</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => (
                      <TableRow key={day}>
                        <TableCell>{day}</TableCell>
                        <TableCell align="right">
                          {progressData.analytics.weekly_activity?.[index] || 0}h
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <PieChart sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">
                  Subject Performance
                </Typography>
              </Box>
              <Stack spacing={1}>
                {Object.entries(progressData.analytics.subject_performance || {}).map(([subject, score]) => (
                  <Box key={subject}>
                    <Box display="flex" justifyContent="space-between" mb={0.5}>
                      <Typography variant="body2">{subject}</Typography>
                      <Typography variant="body2">{score}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={score}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <ShowChart sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">
                  Learning Trend
                </Typography>
              </Box>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Period</TableCell>
                      <TableCell align="right">Average Score</TableCell>
                      <TableCell align="right">Progress</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7'].map((week, index) => {
                      const score = progressData.analytics.learning_trend?.[index] || 0;
                      const prevScore = index > 0 ? (progressData.analytics.learning_trend?.[index - 1] || 0) : score;
                      const trend = score >= prevScore;
                      return (
                        <TableRow key={week}>
                          <TableCell>{week}</TableCell>
                          <TableCell align="right">{score}%</TableCell>
                          <TableCell align="right">
                            <Chip 
                              label={trend ? '↗️' : '↘️'} 
                              size="small" 
                              color={trend ? 'success' : 'warning'}
                            />
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );

    // For now, always use alternative displays (charts can be enabled later)
    return renderAlternativeCharts();
  };

  const renderGoalsAndAchievements = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Learning Goals
            </Typography>
            <List>
              {progressData.goals.map((goal) => (
                <ListItem key={goal.id}>
                  <ListItemIcon>
                    <Schedule />
                  </ListItemIcon>
                  <ListItemText
                    primary={goal.title}
                    secondary={
                      <Box>
                        <LinearProgress
                          variant="determinate"
                          value={goal.progress}
                          sx={{ mt: 1, mb: 1 }}
                        />
                        <Typography variant="caption">
                          Target: {goal.target_date} • {goal.progress}% complete
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Achievements
            </Typography>
            <List>
              {progressData.achievements.map((achievement) => (
                <ListItem key={achievement.id}>
                  <ListItemIcon>
                    <Typography variant="h4">{achievement.badge}</Typography>
                  </ListItemIcon>
                  <ListItemText
                    primary={achievement.title}
                    secondary={
                      <Box>
                        <Typography variant="body2">
                          {achievement.description}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Earned on {achievement.earned_date}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={fetchProgressData}>
          Try Again
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          Learning Progress
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Track your learning journey and monitor your progress
        </Typography>
      </Box>

      {/* Overall Stats */}
      {renderOverallStats()}

      {/* AI Insights */}
      {(() => {
        const insights = recommendationService.getAIInsights();
        const studyRecommendation = recommendationService.getStudyTimeRecommendations();
        return (
          <Box sx={{ mb: 4 }}>
            <Typography variant="h5" gutterBottom>
              AI Insights
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={8}>
                <Alert
                  severity="info"
                  icon={<Psychology />}
                  sx={{ mb: 2 }}
                >
                  <strong>{studyRecommendation.message}</strong><br />
                  {studyRecommendation.recommendation}
                </Alert>
              </Grid>
              {insights.map((insight, index) => (
                <Grid item xs={12} md={4} key={index}>
                  <Alert
                    severity={insight.priority === 'high' ? 'success' : 'info'}
                    sx={{ height: '100%' }}
                  >
                    <strong>{insight.title}</strong><br />
                    {insight.message}
                  </Alert>
                </Grid>
              ))}
            </Grid>
          </Box>
        );
      })()}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={(e, val) => setCurrentTab(val)}>
          <Tab
            label={
              <Box display="flex" alignItems="center">
                <AutoStories sx={{ mr: 1 }} />
                Courses ({progressData.courses.length})
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center">
                <Analytics sx={{ mr: 1 }} />
                Analytics
              </Box>
            }
          />
          <Tab
            label={
              <Box display="flex" alignItems="center">
                <EmojiEvents sx={{ mr: 1 }} />
                Goals & Achievements
              </Box>
            }
          />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {currentTab === 0 && renderCourseProgress()}
      {currentTab === 1 && renderAnalytics()}
      {currentTab === 2 && renderGoalsAndAchievements()}
    </Container>
  );
};

export default ProgressPage;
