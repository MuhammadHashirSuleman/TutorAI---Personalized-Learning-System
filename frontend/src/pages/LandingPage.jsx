import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Box,
  Grid,
  Card,
  CardContent,
  Paper,
  Chip,
  useTheme,
  useMediaQuery,
  Divider,
  IconButton,
  Link,
  TextField,
  Alert,
  Snackbar,
  Avatar
} from '@mui/material';
import {
  School,
  Psychology,
  Analytics,
  AutoStories,
  QuestionAnswer,
  TrendingUp,
  MenuBook,
  Speed,
  Security,
  CloudQueue,
  Facebook,
  Twitter,
  LinkedIn,
  GitHub,
  Email,
  Phone,
  LocationOn,
  Check,
  Send,
  Star
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  
  // Contact form state
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [showContactAlert, setShowContactAlert] = useState(false);
  const [contactSubmitting, setContactSubmitting] = useState(false);

  const features = [
    {
      icon: <Psychology sx={{ fontSize: 40, color: '#10b981' }} />,
      title: 'AI-Powered Learning',
      description: 'Personalized learning paths powered by advanced AI algorithms that adapt to your learning style and pace.',
      highlight: 'Smart AI'
    },
    {
      icon: <Analytics sx={{ fontSize: 40, color: '#10b981' }} />,
      title: 'Progress Analytics',
      description: 'Detailed analytics and insights to track your learning progress and identify areas for improvement.',
      highlight: 'Real-time Analytics'
    },
    {
      icon: <QuestionAnswer sx={{ fontSize: 40, color: '#10b981' }} />,
      title: 'Interactive AI Tutor',
      description: 'Get instant help from our AI tutor that can answer questions and provide explanations 24/7.',
      highlight: '24/7 Support'
    },
    {
      icon: <AutoStories sx={{ fontSize: 40, color: '#10b981' }} />,
      title: 'Document Summarizer',
      description: 'Upload documents and get AI-generated summaries to enhance your learning efficiency.',
      highlight: 'Smart Summaries'
    },
    {
      icon: <TrendingUp sx={{ fontSize: 40, color: '#10b981' }} />,
      title: 'Adaptive Assessments',
      description: 'Dynamic quizzes and assessments that adapt to your knowledge level for optimal learning.',
      highlight: 'Adaptive Testing'
    },
    {
      icon: <MenuBook sx={{ fontSize: 40, color: '#10b981' }} />,
      title: 'Smart Notes',
      description: 'Organize and manage your study notes with AI-enhanced features for better retention.',
      highlight: 'Enhanced Notes'
    }
  ];

  const benefits = [
    {
      icon: <Speed sx={{ fontSize: 30, color: '#10b981' }} />,
      title: 'Accelerated Learning',
      description: 'Learn 3x faster with our AI-optimized curriculum'
    },
    {
      icon: <Security sx={{ fontSize: 30, color: '#10b981' }} />,
      title: 'Secure & Private',
      description: 'Your data is encrypted and protected with enterprise-grade security'
    },
    {
      icon: <CloudQueue sx={{ fontSize: 30, color: '#10b981' }} />,
      title: 'Cloud-Based',
      description: 'Access your learning materials from anywhere, anytime'
    }
  ];

  // Contact form handlers
  const handleContactChange = (e) => {
    setContactForm({
      ...contactForm,
      [e.target.name]: e.target.value
    });
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    setContactSubmitting(true);
    
    // Simulate API call
    setTimeout(() => {
      setShowContactAlert(true);
      setContactForm({ name: '', email: '', message: '' });
      setContactSubmitting(false);
    }, 1000);
  };

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh' }}>
      {/* Header */}
      <AppBar 
        position="sticky" 
        elevation={0} 
        sx={{ 
          backgroundColor: '#000000',
          borderRadius: 0,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
        }}
      >
        <Toolbar sx={{ minHeight: '70px', px: { xs: 2, md: 4 } }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 4 }}>
            <School sx={{ mr: 2, color: '#10b981', fontSize: 32 }} />
            <Typography 
              variant="h6" 
              component="div" 
              sx={{ 
                fontWeight: 'bold', 
                color: 'white',
                fontSize: '1.4rem',
                letterSpacing: '0.5px'
              }}
            >
              TutorAI
            </Typography>
          </Box>
          
          {/* Navigation Links - Centered */}
          <Box sx={{ 
            display: { xs: 'none', md: 'flex' }, 
            gap: 1, 
            flexGrow: 1, 
            justifyContent: 'center',
            ml: 4 
          }}>
            <Button 
              color="inherit" 
              sx={{ 
                fontWeight: 'medium',
                color: 'white',
                px: 3,
                py: 1.5,
                borderRadius: 0,
                textTransform: 'none',
                fontSize: '1rem',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  backgroundColor: 'rgba(16,185,129,0.1)',
                  transform: 'translateY(-1px)'
                }
              }}
            >
              Features
            </Button>
            <Button 
              color="inherit" 
              sx={{ 
                fontWeight: 'medium',
                color: 'white',
                px: 3,
                py: 1.5,
                borderRadius: 0,
                textTransform: 'none',
                fontSize: '1rem',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  backgroundColor: 'rgba(16,185,129,0.1)',
                  transform: 'translateY(-1px)'
                }
              }}
            >
              Pricing
            </Button>
            <Button 
              color="inherit" 
              sx={{ 
                fontWeight: 'medium',
                color: 'white',
                px: 3,
                py: 1.5,
                borderRadius: 0,
                textTransform: 'none',
                fontSize: '1rem',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  backgroundColor: 'rgba(16,185,129,0.1)',
                  transform: 'translateY(-1px)'
                }
              }}
            >
              About
            </Button>
            <Button 
              color="inherit" 
              sx={{ 
                fontWeight: 'medium',
                color: 'white',
                px: 3,
                py: 1.5,
                borderRadius: 0,
                textTransform: 'none',
                fontSize: '1rem',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  backgroundColor: 'rgba(16,185,129,0.1)',
                  transform: 'translateY(-1px)'
                }
              }}
            >
              Contact
            </Button>
          </Box>
          
          {/* Auth Buttons */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button 
              color="inherit" 
              onClick={() => navigate('/login')}
              sx={{ 
                fontWeight: 'medium',
                color: 'white',
                px: 3,
                py: 1.5,
                borderRadius: 0,
                textTransform: 'none',
                fontSize: '1rem',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  transform: 'translateY(-1px)'
                }
              }}
            >
              Login
            </Button>
            <Button 
              variant="outlined" 
              onClick={() => navigate('/register')}
              sx={{ 
                borderColor: '#10b981',
                color: '#10b981',
                px: 4,
                py: 1.5,
                borderRadius: 0,
                borderWidth: '2px',
                textTransform: 'none',
                fontSize: '1rem',
                fontWeight: 'bold',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  backgroundColor: 'rgba(16,185,129,0.1)',
                  borderColor: '#10b981',
                  transform: 'translateY(-2px)',
                  boxShadow: '0px 8px 25px rgba(16,185,129,0.3)'
                }
              }}
            >
              Get Started
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #10b981 0%, #000000 100%)',
          color: 'white',
          py: { xs: 8, md: 12 },
          textAlign: 'center'
        }}
      >
        <Container maxWidth="lg">
          <Typography 
            variant={isMobile ? 'h3' : 'h2'} 
            component="h1" 
            gutterBottom
            sx={{ 
              fontWeight: 'bold', 
              mb: 3,
              animation: 'fadeInUp 1s cubic-bezier(0.4, 0, 0.2, 1)',
              '@keyframes fadeInUp': {
                '0%': {
                  opacity: 0,
                  transform: 'translateY(30px)'
                },
                '100%': {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              }
            }}
          >
            Transform Your Learning with AI
          </Typography>
          <Typography 
            variant={isMobile ? 'h6' : 'h5'} 
            sx={{ 
              mb: 4, 
              opacity: 0.9, 
              maxWidth: '800px', 
              mx: 'auto',
              animation: 'fadeInUp 1s cubic-bezier(0.4, 0, 0.2, 1) 0.3s both',
              '@keyframes fadeInUp': {
                '0%': {
                  opacity: 0,
                  transform: 'translateY(30px)'
                },
                '100%': {
                  opacity: 0.9,
                  transform: 'translateY(0)'
                }
              }
            }}
          >
            Experience personalized education powered by cutting-edge artificial intelligence. 
            Adaptive learning paths, instant AI tutoring, and comprehensive progress tracking.
          </Typography>
          <Box 
            sx={{ 
              display: 'flex', 
              gap: 3, 
              justifyContent: 'center', 
              flexWrap: 'wrap',
              animation: 'fadeInUp 1s cubic-bezier(0.4, 0, 0.2, 1) 0.6s both',
              '@keyframes fadeInUp': {
                '0%': {
                  opacity: 0,
                  transform: 'translateY(30px)'
                },
                '100%': {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              }
            }}
          >
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/register')}
              sx={{
                backgroundColor: 'white',
                color: '#000000',
                px: 6,
                py: 2,
                fontSize: '1.2rem',
                fontWeight: 'bold',
                borderRadius: '8px',
                boxShadow: '0px 4px 15px rgba(0,0,0,0.1)',
                textTransform: 'none',
                transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  transform: 'translateY(-3px) scale(1.05)',
                  boxShadow: '0px 12px 35px rgba(0,0,0,0.2)'
                }
              }}
            >
              Get Started Free
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/login')}
              sx={{
                borderColor: '#10b981',
                color: '#10b981',
                px: 6,
                py: 2,
                fontSize: '1.2rem',
                fontWeight: 'bold',
                borderRadius: '8px',
                borderWidth: '2px',
                textTransform: 'none',
                transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  backgroundColor: 'rgba(16,185,129,0.1)',
                  borderColor: '#10b981',
                  transform: 'translateY(-3px) scale(1.05)',
                  boxShadow: '0px 12px 35px rgba(16,185,129,0.3)'
                }
              }}
            >
              Login
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 8, md: 12 } }}>
        <Box textAlign="center" sx={{ mb: 8 }}>
          <Typography 
            variant="h3" 
            component="h2" 
            gutterBottom 
            sx={{ 
              fontWeight: 'bold',
              animation: 'fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
              '@keyframes fadeInUp': {
                '0%': {
                  opacity: 0,
                  transform: 'translateY(30px)'
                },
                '100%': {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              }
            }}
          >
            Powerful Features
          </Typography>
          <Typography 
            variant="h6" 
            color="text.secondary" 
            sx={{ 
              maxWidth: '600px', 
              mx: 'auto',
              animation: 'fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both',
              '@keyframes fadeInUp': {
                '0%': {
                  opacity: 0,
                  transform: 'translateY(30px)'
                },
                '100%': {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              }
            }}
          >
            Discover the advanced tools and technologies that make our AI learning platform extraordinary
          </Typography>
        </Box>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <Card 
                elevation={2}
                sx={{ 
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  animation: `fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${0.1 * index}s both`,
                  transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                  '&:hover': {
                    transform: 'translateY(-12px) scale(1.02)',
                    boxShadow: '0px 25px 50px -12px rgba(0, 0, 0, 0.25)'
                  },
                  '@keyframes fadeInUp': {
                    '0%': {
                      opacity: 0,
                      transform: 'translateY(40px)'
                    },
                    '100%': {
                      opacity: 1,
                      transform: 'translateY(0)'
                    }
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1, p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {feature.icon}
                    <Chip 
                      label={feature.highlight} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                      sx={{ ml: 'auto' }}
                    />
                  </Box>
                  <Typography variant="h5" component="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
                    {feature.title}
                  </Typography>
                  <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Benefits Section */}
      <Paper elevation={0} sx={{ backgroundColor: '#f9fafb', py: { xs: 8, md: 12 } }}>
        <Container maxWidth="lg">
          <Box textAlign="center" sx={{ mb: 8 }}>
            <Typography 
              variant="h3" 
              component="h2" 
              gutterBottom 
              sx={{ 
                fontWeight: 'bold',
                animation: 'fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                '@keyframes fadeInUp': {
                  '0%': {
                    opacity: 0,
                    transform: 'translateY(30px)'
                  },
                  '100%': {
                    opacity: 1,
                    transform: 'translateY(0)'
                  }
                }
              }}
            >
              Why Choose Our Platform?
            </Typography>
          </Box>
          
          <Grid container spacing={6} alignItems="center">
            {benefits.map((benefit, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Box 
                  textAlign="center"
                  sx={{
                    animation: `fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) ${0.2 * index}s both`,
                    '@keyframes fadeInUp': {
                      '0%': {
                        opacity: 0,
                        transform: 'translateY(40px)'
                      },
                      '100%': {
                        opacity: 1,
                        transform: 'translateY(0)'
                      }
                    }
                  }}
                >
                  <Paper 
                    elevation={0}
                    sx={{ 
                      p: 3,
                      borderRadius: 3,
                      backgroundColor: 'white',
                      border: `2px solid ${theme.palette.divider}`,
                      transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
                      '&:hover': {
                        transform: 'translateY(-5px)',
                        boxShadow: '0px 15px 35px rgba(0, 0, 0, 0.1)',
                        borderColor: '#10b981'
                      }
                    }}
                  >
                    {benefit.icon}
                    <Typography variant="h6" component="h4" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
                      {benefit.title}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {benefit.description}
                    </Typography>
                  </Paper>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Paper>

      {/* Pricing Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 8, md: 12 } }}>
        <Box textAlign="center" mb={6}>
          <Typography 
            variant="h3" 
            component="h2" 
            gutterBottom 
            sx={{ fontWeight: 'bold' }}
          >
            Simple, Transparent Pricing
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Choose the plan that's right for you
          </Typography>
        </Box>
        
        <Grid container spacing={4} justifyContent="center">
          {/* Free Plan */}
          <Grid item xs={12} md={6}>
            <Card 
              elevation={3}
              sx={{ 
                p: 3,
                borderRadius: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: theme.shadows[12]
                }
              }}
            >
              <Box textAlign="center" mb={3}>
                <Avatar
                  sx={{
                    width: 64,
                    height: 64,
                    mx: 'auto',
                    mb: 2,
                    backgroundColor: '#e0f2fe',
                    color: '#01579b'
                  }}
                >
                  <School fontSize="large" />
                </Avatar>
                <Typography variant="h4" component="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Free
                </Typography>
                <Typography variant="h2" component="span" sx={{ fontWeight: 'bold', color: '#10b981' }}>
                  $0
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  /month
                </Typography>
              </Box>
              
              <Box flexGrow={1} mb={3}>
                <Typography variant="body1" color="text.secondary" mb={3}>
                  Perfect for students getting started with AI learning
                </Typography>
                
                {[
                  'AI Tutor (50 queries/month)',
                  'Document Summarizer (10 docs/month)',
                  'Basic Progress Tracking',
                  'Notes Management',
                  'Community Support'
                ].map((feature, index) => (
                  <Box key={index} display="flex" alignItems="center" mb={1.5}>
                    <Check sx={{ color: '#10b981', mr: 2 }} />
                    <Typography variant="body2">{feature}</Typography>
                  </Box>
                ))}
              </Box>
              
              <Button
                variant="outlined"
                fullWidth
                size="large"
                onClick={() => navigate('/register')}
                sx={{
                  py: 1.5,
                  borderColor: '#10b981',
                  color: '#10b981',
                  '&:hover': {
                    borderColor: '#059669',
                    backgroundColor: 'rgba(16, 185, 129, 0.04)'
                  }
                }}
              >
                Get Started Free
              </Button>
            </Card>
          </Grid>
          
          {/* Pro Plan */}
          <Grid item xs={12} md={6}>
            <Card 
              elevation={8}
              sx={{ 
                p: 3,
                borderRadius: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 20px 40px rgba(16, 185, 129, 0.3)'
                }
              }}
            >
              <Chip
                label="MOST POPULAR"
                sx={{
                  position: 'absolute',
                  top: -8,
                  left: '50%',
                  transform: 'translateX(-50%)',
                  backgroundColor: '#fbbf24',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '0.8rem'
                }}
              />
              
              <Box textAlign="center" mb={3}>
                <Avatar
                  sx={{
                    width: 64,
                    height: 64,
                    mx: 'auto',
                    mb: 2,
                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                    color: 'white'
                  }}
                >
                  <Star fontSize="large" />
                </Avatar>
                <Typography variant="h4" component="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
                  Pro
                </Typography>
                <Typography variant="h2" component="span" sx={{ fontWeight: 'bold' }}>
                  $19
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9 }}>
                  /month
                </Typography>
              </Box>
              
              <Box flexGrow={1} mb={3}>
                <Typography variant="body1" sx={{ mb: 3, opacity: 0.9 }}>
                  Unlock the full potential of AI-powered learning
                </Typography>
                
                {[
                  'Unlimited AI Tutor queries',
                  'Unlimited Document Summarizer',
                  'Advanced Progress Analytics',
                  'Priority Support',
                  'Custom Learning Paths',
                  'Export & Sync Features',
                  'Advanced Note Features'
                ].map((feature, index) => (
                  <Box key={index} display="flex" alignItems="center" mb={1.5}>
                    <Check sx={{ color: 'white', mr: 2 }} />
                    <Typography variant="body2" sx={{ opacity: 0.95 }}>{feature}</Typography>
                  </Box>
                ))}
              </Box>
              
              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={() => navigate('/register')}
                sx={{
                  py: 1.5,
                  backgroundColor: 'white',
                  color: '#10b981',
                  fontWeight: 'bold',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    transform: 'scale(1.02)'
                  }
                }}
              >
                Start Pro Trial
              </Button>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Contact Section */}
      <Paper elevation={0} sx={{ backgroundColor: '#f8fafc', py: { xs: 8, md: 12 } }}>
        <Container maxWidth="md">
          <Box textAlign="center" mb={6}>
            <Typography 
              variant="h3" 
              component="h2" 
              gutterBottom 
              sx={{ fontWeight: 'bold' }}
            >
              Get in Touch
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Have questions? We'd love to hear from you.
            </Typography>
          </Box>
          
          <Card elevation={4} sx={{ p: 4, borderRadius: 3 }}>
            <form onSubmit={handleContactSubmit}>
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Your Name"
                    name="name"
                    value={contactForm.name}
                    onChange={handleContactChange}
                    required
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '&:hover fieldset': {
                          borderColor: '#10b981'
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#10b981'
                        }
                      }
                    }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    name="email"
                    type="email"
                    value={contactForm.email}
                    onChange={handleContactChange}
                    required
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '&:hover fieldset': {
                          borderColor: '#10b981'
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#10b981'
                        }
                      }
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Message"
                    name="message"
                    multiline
                    rows={4}
                    value={contactForm.message}
                    onChange={handleContactChange}
                    required
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        '&:hover fieldset': {
                          borderColor: '#10b981'
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#10b981'
                        }
                      }
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    fullWidth
                    disabled={contactSubmitting}
                    startIcon={<Send />}
                    sx={{
                      py: 1.5,
                      backgroundColor: '#10b981',
                      '&:hover': {
                        backgroundColor: '#059669'
                      }
                    }}
                  >
                    {contactSubmitting ? 'Sending...' : 'Send Message'}
                  </Button>
                </Grid>
              </Grid>
            </form>
          </Card>
        </Container>
      </Paper>

      {/* Success Snackbar */}
      <Snackbar
        open={showContactAlert}
        autoHideDuration={6000}
        onClose={() => setShowContactAlert(false)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert 
          onClose={() => setShowContactAlert(false)} 
          severity="success" 
          variant="filled"
          sx={{ width: '100%' }}
        >
          Thank you for your message! We'll get back to you soon.
        </Alert>
      </Snackbar>

      {/* CTA Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 8, md: 12 } }}>
        <Paper 
          elevation={0}
          sx={{ 
            p: { xs: 4, md: 8 },
            textAlign: 'center',
            background: 'linear-gradient(135deg, #10b981 0%, #000000 100%)',
            color: 'white',
            borderRadius: 4,
            animation: 'fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
            '@keyframes fadeInUp': {
              '0%': {
                opacity: 0,
                transform: 'translateY(40px)'
              },
              '100%': {
                opacity: 1,
                transform: 'translateY(0)'
              }
            }
          }}
        >
          <Typography 
            variant="h3" 
            component="h2" 
            gutterBottom 
            sx={{ 
              fontWeight: 'bold',
              animation: 'fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both',
              '@keyframes fadeInUp': {
                '0%': {
                  opacity: 0,
                  transform: 'translateY(30px)'
                },
                '100%': {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              }
            }}
          >
            Ready to Start Learning?
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              mb: 4, 
              opacity: 0.9,
              animation: 'fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.4s both',
              '@keyframes fadeInUp': {
                '0%': {
                  opacity: 0,
                  transform: 'translateY(30px)'
                },
                '100%': {
                  opacity: 0.9,
                  transform: 'translateY(0)'
                }
              }
            }}
          >
            Join thousands of students already transforming their education with AI
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/register')}
            sx={{
              backgroundColor: 'white',
              color: '#000000',
              px: 8,
              py: 2.5,
              fontSize: '1.3rem',
              fontWeight: 'bold',
              borderRadius: '12px',
              textTransform: 'none',
              boxShadow: '0px 8px 25px rgba(255,255,255,0.2)',
              animation: 'fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.6s both',
              transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
              '&:hover': {
                backgroundColor: 'rgba(255,255,255,0.95)',
                transform: 'translateY(-4px) scale(1.05)',
                boxShadow: '0px 15px 40px rgba(255,255,255,0.3)'
              },
              '@keyframes fadeInUp': {
                '0%': {
                  opacity: 0,
                  transform: 'translateY(30px)'
                },
                '100%': {
                  opacity: 1,
                  transform: 'translateY(0)'
                }
              }
            }}
          >
            Start Your Journey
          </Button>
        </Paper>
      </Container>

      {/* Footer */}
      <Box component="footer" sx={{ backgroundColor: '#000000', color: 'white', py: 6 }}>
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <School sx={{ mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  TutorAI
                </Typography>
              </Box>
              <Typography variant="body2" color="grey.400" sx={{ mb: 3, lineHeight: 1.7 }}>
                Revolutionizing education through artificial intelligence. 
                Personalized learning experiences for every student.
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <IconButton color="inherit" size="small">
                  <Facebook />
                </IconButton>
                <IconButton color="inherit" size="small">
                  <Twitter />
                </IconButton>
                <IconButton color="inherit" size="small">
                  <LinkedIn />
                </IconButton>
                <IconButton color="inherit" size="small">
                  <GitHub />
                </IconButton>
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={6} md={2}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Platform
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Link href="#" color="grey.400" underline="hover">Features</Link>
                <Link href="#" color="grey.400" underline="hover">Pricing</Link>
                <Link href="#" color="grey.400" underline="hover">Security</Link>
                <Link href="#" color="grey.400" underline="hover">API</Link>
              </Box>
            </Grid>

            <Grid item xs={12} sm={6} md={2}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Resources
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Link href="#" color="grey.400" underline="hover">Documentation</Link>
                <Link href="#" color="grey.400" underline="hover">Tutorials</Link>
                <Link href="#" color="grey.400" underline="hover">Blog</Link>
                <Link href="#" color="grey.400" underline="hover">Community</Link>
              </Box>
            </Grid>

            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Contact Us
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Email fontSize="small" />
                  <Typography variant="body2" color="grey.400">
                    info@ailearning.com
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Phone fontSize="small" />
                  <Typography variant="body2" color="grey.400">
                    +1 (555) 123-4567
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <LocationOn fontSize="small" />
                  <Typography variant="body2" color="grey.400">
                    San Francisco, CA
                  </Typography>
                </Box>
              </Box>
            </Grid>
          </Grid>

          <Divider sx={{ my: 4, backgroundColor: 'grey.700' }} />
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Typography variant="body2" color="grey.400">
              © 2024 AI Learning System. All rights reserved.
            </Typography>
            <Box sx={{ display: 'flex', gap: 3 }}>
              <Link href="#" color="grey.400" underline="hover" variant="body2">
                Privacy Policy
              </Link>
              <Link href="#" color="grey.400" underline="hover" variant="body2">
                Terms of Service
              </Link>
              <Link href="#" color="grey.400" underline="hover" variant="body2">
                Cookie Policy
              </Link>
            </Box>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;
