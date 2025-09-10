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
  Chip,
  Grid,
  Box,
  Alert,
  CircularProgress,
  LinearProgress,
  Avatar,
  Paper,
} from '@mui/material';
import {
  EmojiEvents as Trophy,
  Star,
  CardGiftcard as Gift,
  Celebration,
  CheckCircle,
  Lock,
} from '@mui/icons-material';
import apiService from '../../services/apiService';

const MilestoneRewards = () => {
  const [milestones, setMilestones] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [rewardDialogOpen, setRewardDialogOpen] = useState(false);
  const [selectedReward, setSelectedReward] = useState(null);

  const loadMilestones = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Mock milestone data
      const mockMilestones = [
        {
          id: 1,
          title: 'First Steps',
          description: 'Complete your first study session',
          category: 'study',
          points_required: 10,
          user_points: 15,
          is_unlocked: true,
          is_claimed: true,
          reward: {
            type: 'badge',
            name: 'Beginner Badge',
            description: 'Your first achievement!',
            icon_url: null
          },
          unlocked_at: '2024-01-15T10:00:00Z'
        },
        {
          id: 2,
          title: 'Note Master',
          description: 'Create 10 comprehensive study notes',
          category: 'notes',
          points_required: 100,
          user_points: 85,
          is_unlocked: false,
          is_claimed: false,
          reward: {
            type: 'points',
            value: 50,
            name: 'Bonus Points',
            description: 'Extra points for your dedication!'
          },
          progress_percentage: 85
        },
        {
          id: 3,
          title: 'Course Crusher',
          description: 'Complete 5 courses with 80% or higher score',
          category: 'courses',
          points_required: 500,
          user_points: 320,
          is_unlocked: false,
          is_claimed: false,
          reward: {
            type: 'feature_unlock',
            name: 'Premium Features',
            description: 'Unlock advanced study tools!'
          },
          progress_percentage: 64
        },
        {
          id: 4,
          title: 'Streak Legend',
          description: 'Maintain a 30-day learning streak',
          category: 'streak',
          points_required: 300,
          user_points: 180,
          is_unlocked: false,
          is_claimed: false,
          reward: {
            type: 'title',
            name: 'Learning Legend',
            description: 'Display this prestigious title on your profile!'
          },
          progress_percentage: 60
        }
      ];

      const mockDashboard = {
        total_milestones: 4,
        unlocked_milestones: 1,
        claimed_rewards: 1,
        total_points: 15,
        next_milestone: mockMilestones.find(m => !m.is_unlocked),
        recent_rewards: mockMilestones.filter(m => m.is_claimed).slice(0, 3)
      };
      
      setMilestones(mockMilestones);
      setDashboard(mockDashboard);
      
    } catch (err) {
      console.error('Error loading milestones:', err);
      setError(err.message || 'Failed to load milestones');
    } finally {
      setLoading(false);
    }
  };

  const claimReward = async (milestoneId) => {
    try {
      setMilestones(milestones.map(m => 
        m.id === milestoneId ? { ...m, is_claimed: true } : m
      ));
      
      // Show celebration effect
      const milestone = milestones.find(m => m.id === milestoneId);
      setSelectedReward(milestone?.reward);
      setRewardDialogOpen(true);
      
    } catch (err) {
      console.error('Error claiming reward:', err);
      setError('Failed to claim reward');
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      study: 'primary',
      notes: 'success',
      courses: 'info',
      streak: 'warning',
      assessment: 'secondary'
    };
    return colors[category] || 'default';
  };

  const getCategoryIcon = (category) => {
    const icons = {
      study: <Trophy />,
      notes: <Star />,
      courses: <CheckCircle />,
      streak: <Celebration />,
      assessment: <Gift />
    };
    return icons[category] || <Trophy />;
  };

  const getRewardIcon = (rewardType) => {
    const icons = {
      badge: <Star color="warning" />,
      points: <Trophy color="primary" />,
      feature_unlock: <Gift color="secondary" />,
      title: <Celebration color="error" />
    };
    return icons[rewardType] || <Gift />;
  };

  useEffect(() => {
    loadMilestones();
  }, []);

  if (loading) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography>Loading milestones...</Typography>
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
    <Box>
      {/* Dashboard Summary */}
      {dashboard && (
        <Card sx={{ 
          mb: 3, 
          background: 'linear-gradient(135deg, #fff3e0 0%, #fce4ec 100%)',
          borderColor: 'warning.light'
        }}>
          <CardHeader 
            title={
              <Box display="flex" alignItems="center" gap={1}>
                <Trophy color="warning" />
                <Typography variant="h6">Milestone Rewards</Typography>
              </Box>
            }
          />
          <CardContent>
            <Grid container spacing={4}>
              <Grid item xs={6} md={3} textAlign="center">
                <Typography variant="h4" color="primary" fontWeight="bold">
                  {dashboard.total_milestones}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Milestones
                </Typography>
              </Grid>
              <Grid item xs={6} md={3} textAlign="center">
                <Typography variant="h4" color="success.main" fontWeight="bold">
                  {dashboard.unlocked_milestones}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Unlocked
                </Typography>
              </Grid>
              <Grid item xs={6} md={3} textAlign="center">
                <Typography variant="h4" color="warning.main" fontWeight="bold">
                  {dashboard.claimed_rewards}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Rewards Claimed
                </Typography>
              </Grid>
              <Grid item xs={6} md={3} textAlign="center">
                <Typography variant="h4" color="info.main" fontWeight="bold">
                  {dashboard.total_points}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Points
                </Typography>
              </Grid>
            </Grid>

            {/* Next Milestone Preview */}
            {dashboard.next_milestone && (
              <Box sx={{ mt: 3, p: 2, bgcolor: 'background.paper', borderRadius: 2 }}>
                <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
                  Next Milestone: {dashboard.next_milestone.title}
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                  <LinearProgress
                    variant="determinate"
                    value={dashboard.next_milestone.progress_percentage}
                    sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                  />
                  <Typography variant="body2">
                    {dashboard.next_milestone.progress_percentage}%
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {dashboard.next_milestone.user_points} / {dashboard.next_milestone.points_required} points
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* Milestones Grid */}
      <Grid container spacing={3}>
        {milestones.map((milestone) => (
          <Grid item xs={12} md={6} key={milestone.id}>
            <Card 
              sx={{ 
                height: '100%',
                position: 'relative',
                border: milestone.is_unlocked ? '2px solid' : '1px solid',
                borderColor: milestone.is_unlocked ? 'success.main' : 'divider',
                opacity: milestone.is_unlocked ? 1 : 0.7
              }}
            >
              <CardHeader
                avatar={
                  <Avatar sx={{ bgcolor: getCategoryColor(milestone.category) + '.main' }}>
                    {getCategoryIcon(milestone.category)}
                  </Avatar>
                }
                title={milestone.title}
                subheader={milestone.description}
                action={
                  <Box>
                    <Chip 
                      label={milestone.category} 
                      color={getCategoryColor(milestone.category)} 
                      size="small" 
                      sx={{ mb: 1 }}
                    />
                    <br />
                    {milestone.is_claimed && (
                      <Chip label="Claimed" color="success" size="small" icon={<CheckCircle />} />
                    )}
                    {milestone.is_unlocked && !milestone.is_claimed && (
                      <Chip label="Ready!" color="warning" size="small" icon={<Gift />} />
                    )}
                    {!milestone.is_unlocked && (
                      <Chip label="Locked" color="default" size="small" icon={<Lock />} />
                    )}
                  </Box>
                }
              />
              
              <CardContent>
                {/* Progress Bar */}
                <Box sx={{ mb: 3 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                    <Typography variant="body2">Progress</Typography>
                    <Typography variant="body2">
                      {milestone.user_points} / {milestone.points_required} points
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={(milestone.user_points / milestone.points_required) * 100} 
                    color={milestone.is_unlocked ? 'success' : 'primary'}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>

                {/* Reward Info */}
                <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                  <Box display="flex" alignItems="center" gap={1} sx={{ mb: 1 }}>
                    {getRewardIcon(milestone.reward.type)}
                    <Typography variant="subtitle2" fontWeight="bold">
                      Reward: {milestone.reward.name}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {milestone.reward.description}
                  </Typography>
                  {milestone.reward.type === 'points' && (
                    <Typography variant="body2" color="primary" fontWeight="bold">
                      +{milestone.reward.value} points
                    </Typography>
                  )}
                </Paper>

                {/* Action Button */}
                <Box sx={{ mt: 2 }}>
                  {milestone.is_unlocked && !milestone.is_claimed && (
                    <Button 
                      variant="contained" 
                      color="success" 
                      fullWidth
                      startIcon={<Gift />}
                      onClick={() => claimReward(milestone.id)}
                    >
                      Claim Reward
                    </Button>
                  )}
                  {milestone.is_claimed && (
                    <Button variant="outlined" fullWidth disabled>
                      Reward Claimed
                    </Button>
                  )}
                  {!milestone.is_unlocked && (
                    <Button variant="outlined" fullWidth disabled>
                      {milestone.points_required - milestone.user_points} points needed
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Reward Claim Dialog */}
      <Dialog 
        open={rewardDialogOpen} 
        onClose={() => setRewardDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ textAlign: 'center' }}>
          <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
            <Celebration sx={{ fontSize: 48, color: 'warning.main' }} />
            <Typography variant="h5">Congratulations!</Typography>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ textAlign: 'center' }}>
          {selectedReward && (
            <Box>
              <Typography variant="h6" sx={{ mb: 1 }}>
                You've earned: {selectedReward.name}
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                {selectedReward.description}
              </Typography>
              {selectedReward.type === 'points' && (
                <Chip 
                  label={`+${selectedReward.value} points`} 
                  color="primary" 
                  size="large"
                />
              )}
            </Box>
          )}
          <Box sx={{ mt: 3 }}>
            <Button 
              variant="contained" 
              onClick={() => setRewardDialogOpen(false)}
              size="large"
            >
              Awesome!
            </Button>
          </Box>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default MilestoneRewards;
