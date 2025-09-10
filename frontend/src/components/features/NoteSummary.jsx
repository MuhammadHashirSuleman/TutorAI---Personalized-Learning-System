import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Grid,
  Box,
  Alert,
  CircularProgress,
  Chip,
  Paper,
  IconButton,
  Divider,
} from '@mui/material';
import {
  NoteAlt as FileText,
  BarChart as BarChart3,
  AccessTime as Clock,
  AutoAwesome as Sparkles,
  Refresh,
  Share,
  Download,
} from '@mui/icons-material';
import apiService from '../../services/apiService';

const NoteSummary = () => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadNoteSummary = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Mock note summary data
      const mockSummary = {
        total_notes: 24,
        total_words: 12840,
        average_length: 535,
        subjects_covered: 8,
        last_updated: '2024-12-09T10:30:00Z',
        recent_notes: [
          {
            id: 1,
            title: 'React Hooks Deep Dive',
            subject: 'Web Development',
            word_count: 892,
            created_at: '2024-12-08T14:20:00Z',
            summary_excerpt: 'Comprehensive overview of useState, useEffect, useContext, and custom hooks with practical examples...'
          },
          {
            id: 2,
            title: 'Machine Learning Algorithms',
            subject: 'Data Science',
            word_count: 1247,
            created_at: '2024-12-07T09:15:00Z',
            summary_excerpt: 'Detailed comparison of supervised vs unsupervised learning, with focus on neural networks and decision trees...'
          },
          {
            id: 3,
            title: 'Database Normalization',
            subject: 'Database Design',
            word_count: 678,
            created_at: '2024-12-06T16:45:00Z',
            summary_excerpt: 'Step-by-step guide to 1NF, 2NF, 3NF, and BCNF with real-world examples and best practices...'
          }
        ],
        subject_breakdown: [
          { subject: 'Web Development', count: 8, percentage: 33 },
          { subject: 'Data Science', count: 6, percentage: 25 },
          { subject: 'Database Design', count: 4, percentage: 17 },
          { subject: 'Software Engineering', count: 3, percentage: 13 },
          { subject: 'UI/UX Design', count: 3, percentage: 12 }
        ],
        productivity_stats: {
          notes_this_week: 5,
          average_per_day: 0.7,
          longest_streak: 12,
          current_streak: 3
        }
      };
      
      setSummary(mockSummary);
      
    } catch (err) {
      console.error('Error loading note summary:', err);
      setError(err.message || 'Failed to load note summary');
    } finally {
      setLoading(false);
    }
  };

  const generateDetailedSummary = async () => {
    try {
      // Mock AI summary generation
      setLoading(true);
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const aiSummary = {
        key_topics: [
          'React Hooks and State Management',
          'Machine Learning Fundamentals',
          'Database Design Principles',
          'Software Architecture Patterns'
        ],
        learning_insights: [
          'Strong focus on frontend technologies (33% of notes)',
          'Growing interest in data science and ML',
          'Consistent note-taking pattern with 3-day current streak',
          'Well-balanced coverage across technical domains'
        ],
        recommendations: [
          'Consider exploring advanced React patterns like context and reducers',
          'Deep dive into specific ML algorithms based on your current foundation',
          'Add more notes on testing methodologies and best practices',
          'Explore system design concepts to complement your current knowledge'
        ]
      };
      
      setSummary(prev => ({ ...prev, ai_summary: aiSummary }));
      
    } catch (err) {
      setError('Failed to generate AI summary');
    } finally {
      setLoading(false);
    }
  };

  const getSubjectColor = (index) => {
    const colors = ['primary', 'secondary', 'success', 'warning', 'info'];
    return colors[index % colors.length];
  };

  useEffect(() => {
    loadNoteSummary();
  }, []);

  if (loading && !summary) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography>Loading note summary...</Typography>
        </CardContent>
      </Card>
    );
  }

  if (error && !summary) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Header Stats */}
      <Card sx={{ mb: 3, background: 'linear-gradient(135deg, #f3e5f5 0%, #e8f5e8 100%)' }}>
        <CardHeader 
          title={
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box display="flex" alignItems="center" gap={1}>
                <FileText color="primary" />
                <Typography variant="h6">Notes Summary</Typography>
              </Box>
              <Box>
                <IconButton onClick={() => loadNoteSummary()}>
                  <Refresh />
                </IconButton>
                <IconButton>
                  <Share />
                </IconButton>
                <IconButton>
                  <Download />
                </IconButton>
              </Box>
            </Box>
          }
        />
        <CardContent>
          <Grid container spacing={3}>
            <Grid item xs={6} md={3} textAlign="center">
              <Typography variant="h4" color="primary" fontWeight="bold">
                {summary?.total_notes}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Notes
              </Typography>
            </Grid>
            <Grid item xs={6} md={3} textAlign="center">
              <Typography variant="h4" color="success.main" fontWeight="bold">
                {summary?.total_words.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Words
              </Typography>
            </Grid>
            <Grid item xs={6} md={3} textAlign="center">
              <Typography variant="h4" color="warning.main" fontWeight="bold">
                {summary?.average_length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Avg Length
              </Typography>
            </Grid>
            <Grid item xs={6} md={3} textAlign="center">
              <Typography variant="h4" color="info.main" fontWeight="bold">
                {summary?.subjects_covered}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Subjects
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
        {/* Recent Notes */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardHeader title="Recent Notes" />
            <CardContent>
              {summary?.recent_notes.map((note, index) => (
                <Box key={note.id}>
                  <Paper sx={{ p: 2, mb: index < summary.recent_notes.length - 1 ? 2 : 0 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="start" sx={{ mb: 1 }}>
                      <Typography variant="h6" fontWeight="bold">
                        {note.title}
                      </Typography>
                      <Chip label={note.subject} color="primary" size="small" />
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {note.summary_excerpt}
                    </Typography>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={2}>
                        <Typography variant="caption" color="text.secondary">
                          <FileText sx={{ fontSize: 16, mr: 0.5 }} />
                          {note.word_count} words
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          <Clock sx={{ fontSize: 16, mr: 0.5 }} />
                          {new Date(note.created_at).toLocaleDateString()}
                        </Typography>
                      </Box>
                      <Button size="small">View Note</Button>
                    </Box>
                  </Paper>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Sidebar Stats */}
        <Grid item xs={12} lg={4}>
          {/* Subject Breakdown */}
          <Card sx={{ mb: 3 }}>
            <CardHeader 
              title="Subject Breakdown"
              avatar={<BarChart3 color="primary" />}
            />
            <CardContent>
              {summary?.subject_breakdown.map((subject, index) => (
                <Box key={subject.subject} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                    <Typography variant="body2" fontWeight="500">
                      {subject.subject}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {subject.count} ({subject.percentage}%)
                    </Typography>
                  </Box>
                  <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1, height: 8 }}>
                    <Box
                      sx={{
                        width: `${subject.percentage}%`,
                        bgcolor: `${getSubjectColor(index)}.main`,
                        height: 8,
                        borderRadius: 1,
                        transition: 'width 0.3s ease'
                      }}
                    />
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>

          {/* Productivity Stats */}
          <Card>
            <CardHeader 
              title="Productivity Stats"
              avatar={<Clock color="success" />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={6} textAlign="center">
                  <Typography variant="h5" color="primary" fontWeight="bold">
                    {summary?.productivity_stats.notes_this_week}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    This Week
                  </Typography>
                </Grid>
                <Grid item xs={6} textAlign="center">
                  <Typography variant="h5" color="success.main" fontWeight="bold">
                    {summary?.productivity_stats.current_streak}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Current Streak
                  </Typography>
                </Grid>
                <Grid item xs={6} textAlign="center">
                  <Typography variant="h5" color="warning.main" fontWeight="bold">
                    {summary?.productivity_stats.average_per_day}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Per Day Avg
                  </Typography>
                </Grid>
                <Grid item xs={6} textAlign="center">
                  <Typography variant="h5" color="info.main" fontWeight="bold">
                    {summary?.productivity_stats.longest_streak}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Best Streak
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* AI Summary Section */}
      <Card sx={{ mt: 3 }}>
        <CardHeader 
          title={
            <Box display="flex" alignItems="center" gap={1}>
              <Sparkles color="secondary" />
              <Typography variant="h6">AI Insights</Typography>
            </Box>
          }
          action={
            !summary?.ai_summary ? (
              <Button 
                variant="contained" 
                startIcon={loading ? <CircularProgress size={20} /> : <Sparkles />}
                onClick={generateDetailedSummary}
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate AI Summary'}
              </Button>
            ) : null
          }
        />
        <CardContent>
          {summary?.ai_summary ? (
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 2 }}>
                  Key Topics
                </Typography>
                {summary.ai_summary.key_topics.map((topic, index) => (
                  <Chip 
                    key={index}
                    label={topic} 
                    variant="outlined" 
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 2 }}>
                  Learning Insights
                </Typography>
                {summary.ai_summary.learning_insights.map((insight, index) => (
                  <Typography 
                    key={index}
                    variant="body2" 
                    sx={{ mb: 1, display: 'flex', alignItems: 'flex-start' }}
                  >
                    • {insight}
                  </Typography>
                ))}
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 2 }}>
                  Recommendations
                </Typography>
                {summary.ai_summary.recommendations.map((rec, index) => (
                  <Typography 
                    key={index}
                    variant="body2" 
                    color="primary"
                    sx={{ mb: 1, display: 'flex', alignItems: 'flex-start' }}
                  >
                    → {rec}
                  </Typography>
                ))}
              </Grid>
            </Grid>
          ) : (
            <Typography variant="body1" color="text.secondary" textAlign="center">
              Generate an AI-powered summary of your notes to get personalized insights and recommendations.
            </Typography>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default NoteSummary;
