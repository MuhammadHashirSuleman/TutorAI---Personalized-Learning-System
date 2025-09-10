import React, { useState } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Paper,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Google,
  GitHub,
  PersonAdd,
  School,
  Psychology,
  AutoStories,
  TrendingUp,
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLoading } from '../../contexts/LoadingContext';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const { showLoading, hideLoading } = useLoading();
  
  const [activeStep, setActiveStep] = useState(0);
  const steps = ['Personal Info', 'Security', 'Preferences', 'Terms'];
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'student',
    educationLevel: '',
    primarySubject: '',
    acceptTerms: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'acceptTerms' ? checked : value,
    }));
  };

  const handleNext = () => {
    setError('');
    
    // Validate current step before proceeding
    if (activeStep === 0) {
      // Personal Info validation
      if (!formData.firstName?.trim()) {
        setError('First name is required');
        return;
      }
      if (!formData.lastName?.trim()) {
        setError('Last name is required');
        return;
      }
      if (!formData.email?.trim()) {
        setError('Email address is required');
        return;
      }
      
      // Email format validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        setError('Please enter a valid email address');
        return;
      }
      
      if (!formData.role) {
        setError('Please select a role');
        return;
      }
    } else if (activeStep === 1) {
      // Security validation
      if (!formData.password) {
        setError('Password is required');
        return;
      }
      if (!formData.confirmPassword) {
        setError('Password confirmation is required');
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        return;
      }
      if (formData.password.length < 8) {
        setError('Password must be at least 8 characters long');
        return;
      }
    }
    
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    console.log('🚀 Starting registration with formData:', formData);
    
    // Enhanced validation with better error messages
    if (!formData.firstName?.trim()) {
      setError('First name is required');
      return;
    }
    if (!formData.lastName?.trim()) {
      setError('Last name is required');
      return;
    }
    if (!formData.email?.trim()) {
      setError('Email address is required');
      return;
    }
    
    // Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return;
    }
    
    if (!formData.password) {
      setError('Password is required');
      return;
    }
    if (!formData.confirmPassword) {
      setError('Password confirmation is required');
      return;
    }
    if (!formData.role) {
      setError('Please select a role');
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    
    if (!formData.acceptTerms) {
      setError('Please accept the terms and conditions');
      return;
    }
    
    try {
      showLoading('Creating your account...');
      console.log('🔄 Calling register function...');
      await register(formData);
      console.log('✅ Registration successful!');
      navigate('/dashboard');
    } catch (err) {
      console.error('❌ Registration failed:', err);
      setError(err.message || 'Failed to create account');
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
        py: 1,
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={4} alignItems="center">
          {/* Left side - Features */}
          <Grid item xs={12} md={7} sx={{ display: { xs: 'none', md: 'block' } }}>
            <Box sx={{ color: 'white' }}>
              <Typography variant="h2" sx={{ 
                fontWeight: 800, 
                mb: 2,
                background: 'linear-gradient(45deg, #fff, #f0f8ff)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}>
                Start Your AI Journey
              </Typography>
              <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
                Join thousands of learners transforming their education with AI
              </Typography>
              
              <Box sx={{ mb: 4 }}>
                {[
                  { icon: <School />, title: '24/7 AI Tutoring', desc: 'Get instant help anytime' },
                  { icon: <TrendingUp />, title: 'Track Progress', desc: 'Monitor your learning journey' },
                  { icon: <Psychology />, title: 'Personalized Learning', desc: 'AI adapts to your style' },
                  { icon: <AutoStories />, title: 'Rich Content Library', desc: 'Access thousands of resources' },
                ].map((feature, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Avatar
                      sx={{
                        bgcolor: 'rgba(255, 255, 255, 0.2)',
                        mr: 3,
                        width: 48,
                        height: 48,
                      }}
                    >
                      {feature.icon}
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        {feature.title}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.8 }}>
                        {feature.desc}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </Box>
          </Grid>
          
          {/* Right side - Multi-step Registration Form */}
          <Grid item xs={12} md={5}>
            {/* Mobile Header */}
            <Box sx={{ display: { xs: 'block', md: 'none' }, textAlign: 'center', mb: 3, color: 'white' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                Start Your AI Journey
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9 }}>
                Join thousands of learners transforming their education
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
                    <PersonAdd fontSize="large" />
                  </Avatar>
                  <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
                    Create Account
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mb={1}>
                    Step {activeStep + 1} of {steps.length}
                  </Typography>
                  
                  {/* Progress bar */}
                  <Box sx={{ width: '100%', mb: 1.5 }}>
                    <LinearProgress 
                      variant="determinate" 
                      value={(activeStep + 1) / steps.length * 100}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                </Box>

                {error && (
                  <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                  </Alert>
                )}

                <form onSubmit={handleSubmit} noValidate>
                  {activeStep === 0 && (
                    <Box>
                      <Typography variant="h6" gutterBottom color="primary" sx={{ mb: 1.5 }}>
                        Personal Information
                      </Typography>
                      <Grid container spacing={1.5}>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="First Name"
                            name="firstName"
                            value={formData.firstName}
                            onChange={handleChange}
                            required
                            size="small"
                            autoComplete="given-name"
                            sx={{ 
                              mb: 1.5,
                              '& .MuiInputBase-input': {
                                fontSize: '16px',
                              },
                              '& .MuiInputLabel-root': {
                                zIndex: 1,
                                pointerEvents: 'none',
                                backgroundColor: '#F8F7FC !important',
                                paddingLeft: '4px',
                                paddingRight: '4px',
                              },
                            }}
                          />
                        </Grid>
                        <Grid item xs={12} sm={6}>
                          <TextField
                            fullWidth
                            label="Last Name"
                            name="lastName"
                            value={formData.lastName}
                            onChange={handleChange}
                            required
                            size="small"
                            autoComplete="family-name"
                            sx={{ 
                              mb: 1.5,
                              '& .MuiInputBase-input': {
                                fontSize: '16px',
                              },
                              '& .MuiInputLabel-root': {
                                zIndex: 1,
                                pointerEvents: 'none',
                                backgroundColor: '#F8F7FC !important',
                                paddingLeft: '4px',
                                paddingRight: '4px',
                              },
                            }}
                          />
                        </Grid>
                      </Grid>
                      <TextField
                        fullWidth
                        label="Email Address"
                        name="email"
                        type="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        size="small"
                        autoComplete="email"
                        sx={{ 
                          mb: 1.5,
                          '& .MuiInputBase-input': {
                            fontSize: '16px',
                          },
                          '& .MuiInputLabel-root': {
                            zIndex: 1,
                            pointerEvents: 'none',
                            backgroundColor: '#F8F7FC !important',
                            paddingLeft: '4px',
                            paddingRight: '4px',
                          },
                        }}
                      />
                      
                      <FormControl fullWidth size="small" sx={{ 
                        mb: 1.5,
                        '& .MuiInputLabel-root': {
                          zIndex: 1,
                          pointerEvents: 'none',
                          backgroundColor: '#F8F7FC !important',
                          paddingLeft: '4px',
                          paddingRight: '4px',
                        },
                      }}>
                        <InputLabel>Role</InputLabel>
                        <Select
                          name="role"
                          value={formData.role}
                          onChange={handleChange}
                          label="Role"
                        >
                          <MenuItem value="student">Student</MenuItem>
                          <MenuItem value="admin">Administrator</MenuItem>
                        </Select>
                      </FormControl>
                    </Box>
                  )}

                  {activeStep === 1 && (
                    <Box>
                      <Typography variant="h6" gutterBottom color="primary" sx={{ mb: 1.5 }}>
                        Security Setup
                      </Typography>
                      <TextField
                        fullWidth
                        label="Password"
                        name="password"
                        type={showPassword ? 'text' : 'password'}
                        value={formData.password}
                        onChange={handleChange}
                        required
                        size="small"
                        autoComplete="new-password"
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
                          mb: 1.5,
                          '& .MuiInputBase-input': {
                            fontSize: '16px',
                          },
                          '& .MuiInputLabel-root': {
                            zIndex: 1,
                            pointerEvents: 'none',
                            backgroundColor: '#F8F7FC !important',
                            paddingLeft: '4px',
                            paddingRight: '4px',
                          },
                        }}
                      />
                      <TextField
                        fullWidth
                        label="Confirm Password"
                        name="confirmPassword"
                        type={showPassword ? 'text' : 'password'}
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        required
                        size="small"
                        autoComplete="new-password"
                        sx={{ 
                          mb: 1.5,
                          '& .MuiInputBase-input': {
                            fontSize: '16px',
                          },
                          '& .MuiInputLabel-root': {
                            zIndex: 1,
                            pointerEvents: 'none',
                            backgroundColor: '#F8F7FC !important',
                            paddingLeft: '4px',
                            paddingRight: '4px',
                          },
                        }}
                      />
                    </Box>
                  )}

                  {activeStep === 2 && (
                    <Box>
                        <Typography variant="h6" gutterBottom color="primary" sx={{ mb: 1.5 }}>
                          Learning Preferences
                        </Typography>
                        <FormControl fullWidth size="small" sx={{ 
                          mb: 1.5,
                          '& .MuiInputLabel-root': {
                            zIndex: 1,
                            pointerEvents: 'none',
                            backgroundColor: '#F8F7FC !important',
                            paddingLeft: '4px',
                            paddingRight: '4px',
                          },
                        }}>
                          <InputLabel>Education Level</InputLabel>
                          <Select
                            name="educationLevel"
                            value={formData.educationLevel}
                            onChange={handleChange}
                            label="Education Level"
                          >
                            <MenuItem value="high-school">High School</MenuItem>
                            <MenuItem value="undergraduate">Undergraduate</MenuItem>
                            <MenuItem value="graduate">Graduate</MenuItem>
                            <MenuItem value="professional">Professional</MenuItem>
                          </Select>
                        </FormControl>
                        
                        <FormControl fullWidth size="small" sx={{ 
                          mb: 1.5,
                          '& .MuiInputLabel-root': {
                            zIndex: 1,
                            pointerEvents: 'none',
                            backgroundColor: '#F8F7FC !important',
                            paddingLeft: '4px',
                            paddingRight: '4px',
                          },
                        }}>
                          <InputLabel>Primary Subject</InputLabel>
                          <Select
                            name="primarySubject"
                            value={formData.primarySubject}
                            onChange={handleChange}
                            label="Primary Subject"
                          >
                            <MenuItem value="mathematics">Mathematics</MenuItem>
                            <MenuItem value="science">Science</MenuItem>
                            <MenuItem value="computer-science">Computer Science</MenuItem>
                            <MenuItem value="languages">Languages</MenuItem>
                            <MenuItem value="business">Business</MenuItem>
                            <MenuItem value="arts">Arts & Humanities</MenuItem>
                            <MenuItem value="other">Other</MenuItem>
                          </Select>
                        </FormControl>
                    </Box>
                  )}

                  {activeStep === 3 && (
                    <Box>
                        <Typography variant="h6" gutterBottom color="primary" sx={{ mb: 1.5 }}>
                          Terms & Conditions
                        </Typography>
                        <Paper sx={{ p: 1.5, mb: 1.5, height: 180, overflow: 'auto' }}>
                          <Typography variant="body2" gutterBottom>
                            Welcome to AI Learning System. By creating an account, you agree to:
                          </Typography>
                          <Typography variant="body2" component="div">
                            • Use our platform responsibly and for educational purposes<br/>
                            • Respect intellectual property rights<br/>
                            • Maintain the security of your account<br/>
                            • Allow us to collect learning analytics to improve your experience<br/>
                            • Receive educational content and updates
                          </Typography>
                        </Paper>
                        
                        <FormControlLabel
                          control={
                            <Checkbox
                              name="acceptTerms"
                              checked={formData.acceptTerms}
                              onChange={handleChange}
                              color="primary"
                            />
                          }
                          label={
                            <Typography variant="body2">
                              I agree to the Terms of Service and Privacy Policy
                            </Typography>
                          }
                        />
                    </Box>
                  )}

                  <Box display="flex" justifyContent="space-between" sx={{ mt: 3 }}>
                    <Button
                      disabled={activeStep === 0}
                      onClick={handleBack}
                      sx={{ mr: 1 }}
                    >
                      Back
                    </Button>
                    <Button
                      type={activeStep === steps.length - 1 ? 'submit' : 'button'}
                      variant="contained"
                      onClick={activeStep === steps.length - 1 ? undefined : handleNext}
                      disabled={activeStep === steps.length - 1 && !formData.acceptTerms}
                      sx={{ minWidth: 120 }}
                    >
                      {activeStep === steps.length - 1 ? 'Create Account' : 'Next'}
                    </Button>
                  </Box>
                </form>


                {activeStep === 0 && (
                  <>
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
                        Already have an account?{' '}
                        <Button component={Link} to="/login" color="primary">
                          Sign in here
                        </Button>
                      </Typography>
                    </Box>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default RegisterPage;
