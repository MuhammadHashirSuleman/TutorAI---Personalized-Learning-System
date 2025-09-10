import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  LinearProgress,
  Chip,
  Grid,
  Box,
  Alert,
  CircularProgress,
  IconButton,
  Paper,
} from '@mui/material';
import {
  Target,
  Add as Plus,
  Event as Calendar,
  EmojiEvents as Trophy,
  Schedule as Clock,
  CheckCircle,
  PlayArrow as Play,
  Pause,
  Edit,
} from '@mui/icons-material';
import apiService from '../../services/apiService';

const GoalsManager = () => {
  const [goals, setGoals] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  // New goal form
  const [newGoal, setNewGoal] = useState({
    title: '',
    description: '',
    goal_type: 'notes',
    target_value: 5,
    unit: 'notes',
    target_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    subject_focus: '',
    difficulty_level: 'medium'
  });

  const loadGoals = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Mock data for goals since API might not be available
      const mockGoals = [
        {
          id: 1,
          title: 'Complete 5 Study Notes',
          description: 'Create comprehensive notes for 5 different topics',
          goal_type: 'notes',
          target_value: 5,
          current_value: 3,
          unit: 'notes',
          status: 'active',
          target_date: '2024-12-31',
          created_at: '2024-01-01',
          progress_percentage: 60,
          is_completed: false
        },
        {
          id: 2,
          title: 'Master JavaScript Fundamentals',
          description: 'Complete JavaScript course and pass assessment',
          goal_type: 'courses',
          target_value: 1,
          current_value: 1,
          unit: 'courses',
          status: 'completed',
          target_date: '2024-11-30',
          created_at: '2024-01-15',
          progress_percentage: 100,
          is_completed: true
        }
      ];

      const mockDashboard = {
        statistics: {
          total_goals: 2,
          completed_goals: 1,
          active_goals: 1,
          completion_rate: 50
        }
      };
      
      setGoals(mockGoals);
      setDashboard(mockDashboard);
      
    } catch (err) {
      console.error('Error loading goals:', err);
      setError(err.message || 'Failed to load goals');
    } finally {
      setLoading(false);
    }
  };

  const createGoal = async () => {
    try {
      const mockNewGoal = {
        id: Date.now(),
        ...newGoal,
        current_value: 0,
        status: 'active',
        created_at: new Date().toISOString(),
        progress_percentage: 0,
        is_completed: false
      };
      
      setGoals([...goals, mockNewGoal]);
      setCreateDialogOpen(false);
      
      // Reset form
      setNewGoal({
        title: '',
        description: '',
        goal_type: 'notes',
        target_value: 5,
        unit: 'notes',
        target_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        subject_focus: '',
        difficulty_level: 'medium'
      });
      
    } catch (err) {
      console.error('Error creating goal:', err);
      setError('Failed to create goal');
    }
  };

  const updateGoalStatus = async (goalId, newStatus) => {
    try {
      setGoals(goals.map(g => 
        g.id === goalId 
          ? { ...g, status: newStatus, is_completed: newStatus === 'completed' }
          : g
      ));
    } catch (err) {
      console.error('Error updating goal:', err);
      setError('Failed to update goal status');
    }
  };

  const getGoalTypeInfo = (type) => {
    const types = {
      notes: { label: 'Notes Creation', unit: 'notes', color: 'primary' },
      courses: { label: 'Course Completion', unit: 'courses', color: 'success' },
      quizzes: { label: 'Quiz Performance', unit: 'quizzes', color: 'secondary' },
      study_time: { label: 'Study Time', unit: 'hours', color: 'warning' },
      streak: { label: 'Learning Streak', unit: 'days', color: 'error' },
      skills: { label: 'Skill Development', unit: 'skills', color: 'info' },
      custom: { label: 'Custom Goal', unit: 'items', color: 'default' },
    };
    return types[type] || types.custom;
  };

  const getStatusColor = (status, isCompleted) => {
    if (isCompleted) return 'success';
    
    const colors = {
      active: 'primary',
      completed: 'success',
      paused: 'warning',
      abandoned: 'error',
    };
    return colors[status] || 'primary';
  };

  useEffect(() => {
    loadGoals();
  }, []);

  if (loading) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography>Loading goals...</Typography>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ space: 3 }}>
      {/* Dashboard Summary */}
      {dashboard && (
        <Card sx={{ 
          mb: 3, 
          background: 'linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%)',
          borderColor: 'primary.light'
        }}>
          <CardHeader 
            title={
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box display="flex" alignItems="center" gap={1}>
                  <Trophy color="primary" />
                  <Typography variant="h6">Goals Dashboard</Typography>
                </Box>
                <Button 
                  variant="contained" 
                  startIcon={<Plus />}
                  onClick={() => setCreateDialogOpen(true)}
                >
                  New Goal
                </Button>
              </Box>
            }
          />
          <CardContent>
            <Grid container spacing={4}>
              <Grid item xs={6} md={3} textAlign="center">
                <Typography variant="h4" color="primary" fontWeight="bold">
                  {dashboard.statistics.total_goals}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Goals
                </Typography>
              </Grid>
              <Grid item xs={6} md={3} textAlign="center">
                <Typography variant="h4" color="success.main" fontWeight="bold">
                  {dashboard.statistics.completed_goals}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Completed
                </Typography>
              </Grid>
              <Grid item xs={6} md={3} textAlign="center">
                <Typography variant="h4" color="warning.main" fontWeight="bold">
                  {dashboard.statistics.active_goals}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active
                </Typography>
              </Grid>
              <Grid item xs={6} md={3} textAlign="center">
                <Typography variant="h4" color="secondary.main" fontWeight="bold">
                  {dashboard.statistics.completion_rate}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Success Rate
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Goals List */}
      <Grid container spacing={3}>
        {goals.map((goal) => {
          const typeInfo = getGoalTypeInfo(goal.goal_type);
          const statusColor = getStatusColor(goal.status, goal.is_completed);
          
          return (
            <Grid item xs={12} md={6} key={goal.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  border: goal.is_completed ? '2px solid' : '1px solid',
                  borderColor: goal.is_completed ? 'success.main' : 'divider'
                }}
              >
                <CardHeader
                  title={goal.title}
                  subheader={typeInfo.label}
                  action={
                    <Box>
                      <Chip 
                        label={goal.status} 
                        color={statusColor} 
                        size="small" 
                        sx={{ mr: 1 }}
                      />
                      {goal.is_completed && <CheckCircle color="success" />}
                    </Box>
                  }
                />
                <CardContent>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {goal.description}
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                      <Typography variant="body2">Progress</Typography>
                      <Typography variant="body2">
                        {goal.current_value} / {goal.target_value} {goal.unit}
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={goal.progress_percentage} 
                      color={statusColor}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {goal.progress_percentage}% Complete
                    </Typography>
                  </Box>

                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="caption" color="text.secondary">
                      Due: {new Date(goal.target_date).toLocaleDateString()}
                    </Typography>
                    <Box>
                      {goal.status === 'active' && !goal.is_completed && (
                        <IconButton 
                          size="small"
                          onClick={() => updateGoalStatus(goal.id, 'paused')}
                        >
                          <Pause />
                        </IconButton>
                      )}
                      {goal.status === 'paused' && (
                        <IconButton 
                          size="small"
                          onClick={() => updateGoalStatus(goal.id, 'active')}
                        >
                          <Play />
                        </IconButton>
                      )}
                      {!goal.is_completed && (
                        <IconButton 
                          size="small"
                          onClick={() => updateGoalStatus(goal.id, 'completed')}
                        >
                          <CheckCircle />
                        </IconButton>
                      )}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Create Goal Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Goal</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Goal Title"
                value={newGoal.title}
                onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={newGoal.description}
                onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Goal Type</InputLabel>
                <Select
                  value={newGoal.goal_type}
                  label="Goal Type"
                  onChange={(e) => setNewGoal({ ...newGoal, goal_type: e.target.value })}
                >
                  <MenuItem value="notes">Notes Creation</MenuItem>
                  <MenuItem value="courses">Course Completion</MenuItem>
                  <MenuItem value="quizzes">Quiz Performance</MenuItem>
                  <MenuItem value="study_time">Study Time</MenuItem>
                  <MenuItem value="streak">Learning Streak</MenuItem>
                  <MenuItem value="skills">Skill Development</MenuItem>
                  <MenuItem value="custom">Custom Goal</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Target Value"
                value={newGoal.target_value}
                onChange={(e) => setNewGoal({ ...newGoal, target_value: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="date"
                label="Target Date"
                value={newGoal.target_date}
                onChange={(e) => setNewGoal({ ...newGoal, target_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Difficulty Level</InputLabel>
                <Select
                  value={newGoal.difficulty_level}
                  label="Difficulty Level"
                  onChange={(e) => setNewGoal({ ...newGoal, difficulty_level: e.target.value })}
                >
                  <MenuItem value="easy">Easy</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="hard">Hard</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Subject Focus (Optional)"
                value={newGoal.subject_focus}
                onChange={(e) => setNewGoal({ ...newGoal, subject_focus: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={createGoal} variant="contained">Create Goal</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default GoalsManager;
