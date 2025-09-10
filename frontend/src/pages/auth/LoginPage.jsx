import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  FormControlLabel,
  Checkbox,
  Divider,
  IconButton,
  InputAdornment,
  Alert,
  Avatar,
  Container,
  Grid,
  Paper,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Google,
  GitHub,
  School,
  Psychology,
  AutoStories,
  TrendingUp,
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLoading } from '../../contexts/LoadingContext';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { showLoading, hideLoading } = useLoading();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [formKey, setFormKey] = useState(Date.now());

  // Prevent autofill and clear form on mount
  useEffect(() => {
    setFormData({
      email: '',
      password: '',
      rememberMe: false,
    });
    // Force form reset
    setFormKey(Date.now());
  }, []);

  const handleChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'rememberMe' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const email = formData.email?.trim();
    const password = formData.password?.trim();
    
    if (!email) {
      setError('Email is required');
      return;
    }
    
    if (!password) {
      setError('Password is required');
      return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }
    
    try {
      showLoading('Signing you in...');
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Failed to sign in');
    } finally {
      hideLoading();
    }
  };

  return (
    <Box
      sx={{
        height: '100vh',
        background: 'linear-gradient(135deg, #10b981 0%, #000000 100%)',
        display: 'flex',
        alignItems: 'center',
        overflow: 'hidden',
        py: 2,
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4} alignItems="center">
          {/* Left side - Features */}
          <Grid item xs={12} md={7} sx={{ display: { xs: 'none', md: 'block' } }}>
            <Box sx={{ color: 'white', mb: 4 }}>
              <Typography variant="h2" sx={{ 
                fontWeight: 800, 
                mb: 2,
                background: 'linear-gradient(45deg, #fff, #f0f8ff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                AI-Powered Learning
              </Typography>
              <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
                Revolutionize your education with personalized AI tutoring
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Paper
                    sx={{
                      p: 3,
                      background: 'rgba(255, 255, 255, 0.1)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                    }}
                  >
                    <Avatar
                      sx={{
                        bgcolor: 'rgba(255, 255, 255, 0.2)',
                        mb: 2,
                        width: 56,
                        height: 56,
                      }}
                    >
                      <Psychology fontSize="large" />
                    </Avatar>
                    <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                      AI Tutoring
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                      Get personalized help from our AI tutor that adapts to your learning style
                    </Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Paper
                    sx={{
                      p: 3,
                      background: 'rgba(255, 255, 255, 0.1)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                    }}
                  >
                    <Avatar
                      sx={{
                        bgcolor: 'rgba(255, 255, 255, 0.2)',
                        mb: 2,
                        width: 56,
                        height: 56,
                      }}
                    >
                      <TrendingUp fontSize="large" />
                    </Avatar>
                    <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                      Progress Tracking
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                      Monitor your learning journey with detailed analytics and insights
                    </Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Paper
                    sx={{
                      p: 3,
                      background: 'rgba(255, 255, 255, 0.1)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                    }}
                  >
                    <Avatar
                      sx={{
                        bgcolor: 'rgba(255, 255, 255, 0.2)',
                        mb: 2,
                        width: 56,
                        height: 56,
                      }}
                    >
                      <AutoStories fontSize="large" />
                    </Avatar>
                    <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                      Adaptive Content
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                      Receive customized learning materials based on your strengths and weaknesses
                    </Typography>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Paper
                    sx={{
                      p: 3,
                      background: 'rgba(255, 255, 255, 0.1)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                    }}
                  >
                    <Avatar
                      sx={{
                        bgcolor: 'rgba(255, 255, 255, 0.2)',
                        mb: 2,
                        width: 56,
                        height: 56,
                      }}
                    >
                      <School fontSize="large" />
                    </Avatar>
                    <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
                      Smart Assessments
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                      Take AI-generated quizzes that target your specific learning needs
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          </Grid>
          
          {/* Right side - Login Form */}
          <Grid item xs={12} md={5}>
            {/* Mobile Header */}
            <Box sx={{ display: { xs: 'block', md: 'none' }, textAlign: 'center', mb: 3, color: 'white' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                AI-Powered Learning
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Welcome back to your learning journey
              </Typography>
            </Box>
            <Card
              sx={{
                maxWidth: 450,
                mx: 'auto',
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box textAlign="center" mb={3}>
                  <Avatar
                    sx={{
                      width: 56,
                      height: 56,
                      mx: 'auto',
                      mb: 1.5,
                      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    }}
                  >
                    <School fontSize="large" />
                  </Avatar>
                  <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
                    Welcome Back
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    Sign in to continue your learning journey
                  </Typography>
                </Box>

                {error && (
                  <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                  </Alert>
                )}

                <form onSubmit={handleSubmit} noValidate key={formKey} autoComplete="off">
                  <TextField
                    fullWidth
                    label="Email Address"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    margin="normal"
                    required
                    autoComplete="new-email"
                    InputLabelProps={{
                      shrink: Boolean(formData.email),
                    }}
                    sx={{ 
                      mb: 2,
                      '& .MuiInputBase-input': {
                        fontSize: '16px',
                      },
                      '& .MuiInputLabel-root': {
                        zIndex: 1,
                        pointerEvents: 'none',
                        backgroundColor: '#F8F7FC !important',
                        paddingLeft: '4px',
                        paddingRight: '4px',
                        '&.Mui-focused, &.MuiFormLabel-filled': {
                          transform: 'translate(14px, -9px) scale(0.75)',
                        },
                      },
                    }}
                  />

                  <TextField
                    fullWidth
                    label="Password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleChange}
                    margin="normal"
                    required
                    autoComplete="new-password"
                    InputLabelProps={{
                      shrink: Boolean(formData.password),
                    }}
                    InputProps={{
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            onClick={() => setShowPassword(!showPassword)}
                            edge="end"
                            size="small"
                          >
                            {showPassword ? <VisibilityOff /> : <Visibility />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    }}
                    sx={{ 
                      mb: 2,
                      '& .MuiInputBase-input': {
                        fontSize: '16px',
                      },
                      '& .MuiInputLabel-root': {
                        zIndex: 1,
                        pointerEvents: 'none',
                        backgroundColor: '#F8F7FC !important',
                        paddingLeft: '4px',
                        paddingRight: '4px',
                        '&.Mui-focused, &.MuiFormLabel-filled': {
                          transform: 'translate(14px, -9px) scale(0.75)',
                        },
                      },
                    }}
                  />

                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          name="rememberMe"
                          checked={formData.rememberMe}
                          onChange={handleChange}
                          color="primary"
                        />
                      }
                      label="Remember me"
                    />
                    <Button color="primary" component={Link} to="/forgot-password">
                      Forgot password?
                    </Button>
                  </Box>

                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    size="large"
                    sx={{ mb: 2, py: 1.2 }}
                  >
                    Sign In
                  </Button>
                </form>

                <Divider sx={{ my: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Or continue with
                  </Typography>
                </Divider>

                <Box display="flex" gap={2} mb={2}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Google />}
                    sx={{ py: 1.2 }}
                  >
                    Google
                  </Button>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<GitHub />}
                    sx={{ py: 1.2 }}
                  >
                    GitHub
                  </Button>
                </Box>

                <Box textAlign="center">
                  <Typography variant="body2" color="text.secondary">
                    Don't have an account?{' '}
                    <Button component={Link} to="/register" color="primary">
                      Sign up now
                    </Button>
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default LoginPage;