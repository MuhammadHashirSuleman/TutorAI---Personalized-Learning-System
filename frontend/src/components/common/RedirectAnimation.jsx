import React, { useEffect, useState } from 'react';
import {
  Dialog,
  DialogContent,
  Box,
  Typography,
  CircularProgress,
  Avatar,
  Fade,
  Zoom,
  Chip,
} from '@mui/material';
import {
  OpenInNew,
  TrendingUp,
  Security,
  School,
  Speed,
} from '@mui/icons-material';
import { keyframes } from '@emotion/react';

// Animation keyframes
const pulseAnimation = keyframes`
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
`;

const slideInAnimation = keyframes`
  0% { transform: translateY(20px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
`;

const rotateAnimation = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const waveAnimation = keyframes`
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
`;

const RedirectAnimation = ({ 
  open, 
  onClose, 
  courseTitle, 
  provider, 
  destinationUrl,
  onRedirect 
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [animationPhase, setAnimationPhase] = useState('preparing');

  // Animation steps
  const steps = React.useMemo(() => [
    { 
      message: 'Preparing your learning journey...', 
      icon: School,
      color: '#6366f1',
      duration: 1000 
    },
    { 
      message: 'Securing connection...', 
      icon: Security,
      color: '#10b981',
      duration: 1200 
    },
    { 
      message: 'Optimizing your experience...', 
      icon: Speed,
      color: '#f59e0b',
      duration: 1000 
    },
    { 
      message: `Redirecting to ${provider}...`, 
      icon: OpenInNew,
      color: '#8b5cf6',
      duration: 1500 
    }
  ], [provider]);

  useEffect(() => {
    if (!open) {
      setCurrentStep(0);
      setAnimationPhase('preparing');
      return;
    }

    console.log('RedirectAnimation: Starting animation sequence');
    console.log('RedirectAnimation: Destination URL:', destinationUrl);
    
    let timeouts = [];
    let totalDelay = 0;

    // Step 1: Preparing (800ms)
    const step1 = setTimeout(() => {
      console.log('RedirectAnimation: Step 1 - Preparing');
      setCurrentStep(0);
      setAnimationPhase('processing');
    }, 0);
    timeouts.push(step1);
    totalDelay = 800;

    // Step 2: Securing (800ms)
    const step2 = setTimeout(() => {
      console.log('RedirectAnimation: Step 2 - Securing');
      setCurrentStep(1);
      setAnimationPhase('processing');
    }, totalDelay);
    timeouts.push(step2);
    totalDelay += 800;

    // Step 3: Optimizing (800ms)
    const step3 = setTimeout(() => {
      console.log('RedirectAnimation: Step 3 - Optimizing');
      setCurrentStep(2);
      setAnimationPhase('processing');
    }, totalDelay);
    timeouts.push(step3);
    totalDelay += 800;

    // Step 4: Redirecting (800ms)
    const step4 = setTimeout(() => {
      console.log('RedirectAnimation: Step 4 - Final redirect step');
      setCurrentStep(3);
      setAnimationPhase('redirecting');
    }, totalDelay);
    timeouts.push(step4);
    totalDelay += 800;

    // Final redirect action
    const redirectTimeout = setTimeout(() => {
      console.log('RedirectAnimation: About to redirect to:', destinationUrl);
      console.log('RedirectAnimation: onRedirect function exists:', !!onRedirect);
      
      if (destinationUrl) {
        if (onRedirect) {
          console.log('RedirectAnimation: Using onRedirect prop');
          onRedirect(destinationUrl);
        } else {
          console.log('RedirectAnimation: onRedirect prop not available, using direct window.open');
          window.open(destinationUrl, '_blank');
        }
        console.log('RedirectAnimation: Redirect initiated successfully');
      } else {
        console.error('RedirectAnimation: No destinationUrl provided!');
        console.error('RedirectAnimation: destinationUrl:', destinationUrl);
      }
      
      // Close the dialog
      onClose();
    }, totalDelay + 300);

    timeouts.push(redirectTimeout);

    // Cleanup function
    return () => {
      console.log('RedirectAnimation: Cleaning up timeouts');
      timeouts.forEach(timeout => clearTimeout(timeout));
    };
  }, [open, destinationUrl, onRedirect, onClose]);

  const getCurrentStep = () => steps[currentStep] || steps[0];
  const currentStepData = getCurrentStep();
  const IconComponent = currentStepData.icon;

  // Provider-specific colors and icons
  const getProviderTheme = (provider) => {
    const themes = {
      'Coursera': { color: '#0066cc', bgColor: '#e6f3ff' },
      'Udemy': { color: '#ec5252', bgColor: '#fef2f2' },
      'LinkedIn Learning': { color: '#0077b5', bgColor: '#eff8ff' },
      'Microsoft': { color: '#00bcf2', bgColor: '#f0f9ff' },
      'NVIDIA': { color: '#76b900', bgColor: '#f0fdf4' },
      'default': { color: '#6366f1', bgColor: '#f8fafc' }
    };
    return themes[provider] || themes.default;
  };

  const providerTheme = getProviderTheme(provider);

  return (
    <Dialog
      open={open}
      onClose={() => {}} // Prevent manual close
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 4,
          overflow: 'hidden',
          background: `linear-gradient(135deg, ${providerTheme.bgColor} 0%, white 100%)`,
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        }
      }}
    >
      <DialogContent sx={{ p: 0, position: 'relative', overflow: 'hidden' }}>
        {/* Background decoration */}
        <Box
          sx={{
            position: 'absolute',
            top: -50,
            right: -50,
            width: 150,
            height: 150,
            borderRadius: '50%',
            background: `linear-gradient(135deg, ${providerTheme.color}20, transparent)`,
            animation: `${pulseAnimation} 2s ease-in-out infinite`,
          }}
        />
        
        <Box
          sx={{
            position: 'absolute',
            bottom: -30,
            left: -30,
            width: 100,
            height: 100,
            borderRadius: '50%',
            background: `linear-gradient(135deg, ${providerTheme.color}15, transparent)`,
            animation: `${rotateAnimation} 8s linear infinite`,
          }}
        />

        <Box
          sx={{
            p: 6,
            textAlign: 'center',
            position: 'relative',
            zIndex: 1,
          }}
        >
          {/* Header */}
          <Fade in={true} timeout={500}>
            <Box sx={{ mb: 4 }}>
              <Avatar
                sx={{
                  width: 80,
                  height: 80,
                  mx: 'auto',
                  mb: 2,
                  background: `linear-gradient(135deg, ${providerTheme.color}, ${providerTheme.color}cc)`,
                  animation: `${pulseAnimation} 2s ease-in-out infinite`,
                }}
              >
                <School sx={{ fontSize: 40 }} />
              </Avatar>
              
              <Typography variant="h4" fontWeight="bold" gutterBottom>
                Launching Course
              </Typography>
              
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {courseTitle}
              </Typography>
              
              <Chip
                label={provider}
                sx={{
                  background: providerTheme.color,
                  color: 'white',
                  fontWeight: 600,
                  px: 2,
                }}
              />
            </Box>
          </Fade>

          {/* Animation Steps */}
          <Box sx={{ mb: 4 }}>
            <Zoom in={true} key={currentStep} timeout={300}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mb: 3,
                }}
              >
                <Avatar
                  sx={{
                    width: 60,
                    height: 60,
                    mr: 2,
                    background: currentStepData.color,
                    animation: animationPhase === 'redirecting' 
                      ? `${rotateAnimation} 1s linear infinite`
                      : `${pulseAnimation} 1.5s ease-in-out infinite`,
                  }}
                >
                  <IconComponent sx={{ fontSize: 30 }} />
                </Avatar>
                
                <Box sx={{ textAlign: 'left' }}>
                  <Typography 
                    variant="h6" 
                    fontWeight="600"
                    sx={{
                      animation: `${slideInAnimation} 0.5s ease-out`,
                    }}
                  >
                    {currentStepData.message}
                  </Typography>
                  
                  <Box display="flex" alignItems="center" mt={1}>
                    <CircularProgress
                      size={16}
                      thickness={4}
                      sx={{ 
                        mr: 1,
                        color: currentStepData.color,
                      }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Step {currentStep + 1} of {steps.length}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </Zoom>

            {/* Progress indicator */}
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'center',
                gap: 1,
                mb: 3,
              }}
            >
              {steps.map((_, index) => (
                <Box
                  key={index}
                  sx={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    background: index <= currentStep ? providerTheme.color : '#e2e8f0',
                    transition: 'all 0.3s ease',
                    transform: index === currentStep ? 'scale(1.2)' : 'scale(1)',
                    animation: index === currentStep ? `${waveAnimation} 1s ease-in-out infinite` : 'none',
                  }}
                />
              ))}
            </Box>
          </Box>

          {/* Security Notice */}
          <Fade in={currentStep >= 1} timeout={500}>
            <Box
              sx={{
                p: 2,
                borderRadius: 2,
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.2)',
                mb: 2,
              }}
            >
              <Box display="flex" alignItems="center" justifyContent="center">
                <Security sx={{ fontSize: 20, color: '#10b981', mr: 1 }} />
                <Typography variant="body2" color="#10b981" fontWeight="500">
                  You are redirecting outside of TutorAI
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                This will open {provider} in a new tab
              </Typography>
            </Box>
          </Fade>

          {/* Fun fact during loading */}
          <Fade in={currentStep >= 2} timeout={500}>
            <Box
              sx={{
                p: 2,
                borderRadius: 2,
                background: 'rgba(139, 92, 246, 0.1)',
                border: '1px solid rgba(139, 92, 246, 0.2)',
              }}
            >
              <Box display="flex" alignItems="center" justifyContent="center" mb={1}>
                <TrendingUp sx={{ fontSize: 20, color: '#8b5cf6', mr: 1 }} />
                <Typography variant="body2" color="#8b5cf6" fontWeight="500">
                  Did you know?
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Students who use external courses alongside teacher-led classes show 
                <strong> 40% better learning outcomes</strong>
              </Typography>
            </Box>
          </Fade>
        </Box>
      </DialogContent>
    </Dialog>
  );
};

export default RedirectAnimation;
