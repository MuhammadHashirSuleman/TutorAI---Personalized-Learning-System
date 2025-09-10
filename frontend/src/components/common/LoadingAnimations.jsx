import React, { useState, useEffect } from 'react';
import {
  Typography,
  Backdrop,
  Paper,
  Box,
  LinearProgress,
  keyframes,
} from '@mui/material';
import { Psychology, AutoAwesome, School, TipsAndUpdates, Lightbulb } from '@mui/icons-material';

// Modern keyframe animations
const breathe = keyframes`
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.1); opacity: 1; }
`;

const morphing = keyframes`
  0% { border-radius: 50%; }
  25% { border-radius: 25%; }
  50% { border-radius: 10%; }
  75% { border-radius: 25%; }
  100% { border-radius: 50%; }
`;

const slideUp = keyframes`
  0% { transform: translateY(100%); opacity: 0; }
  100% { transform: translateY(0%); opacity: 1; }
`;

const waveLoading = keyframes`
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
`;

const skeletonPulse = keyframes`
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
`;

const neuralPulse = keyframes`
  0% { 
    transform: scale(1); 
    background: linear-gradient(45deg, #667eea, #764ba2);
  }
  50% { 
    transform: scale(1.3); 
    background: linear-gradient(45deg, #f093fb, #f5576c);
  }
  100% { 
    transform: scale(1); 
    background: linear-gradient(45deg, #667eea, #764ba2);
  }
`;

// Minimalist modern loader
export const MinimalistLoader = ({ isLoading, message }) => {
  const [dots, setDots] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 500);
    return () => clearInterval(interval);
  }, []);

  if (!isLoading) return null;

  return (
    <Backdrop
      sx={{
        color: '#fff',
        zIndex: (theme) => theme.zIndex.drawer + 1000,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        backdropFilter: 'blur(8px)',
      }}
      open={isLoading}
    >
      <Box
        sx={{
          textAlign: 'center',
          color: 'white',
        }}
      >
        {/* Morphing shape */}
        <Box
          sx={{
            width: 80,
            height: 80,
            mx: 'auto',
            mb: 3,
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            animation: `${morphing} 2s infinite ease-in-out, ${breathe} 3s infinite ease-in-out`,
          }}
        />
        
        <Typography
          variant="h6"
          sx={{
            fontWeight: 300,
            letterSpacing: 2,
            textTransform: 'uppercase',
          }}
        >
          {message || 'Loading'}{dots}
        </Typography>
      </Box>
    </Backdrop>
  );
};

// Neural network inspired loader
export const NeuralNetworkLoader = ({ isLoading, message }) => {
  if (!isLoading) return null;

  return (
    <Backdrop
      sx={{
        color: '#fff',
        zIndex: (theme) => theme.zIndex.drawer + 1000,
        background: 'radial-gradient(circle, rgba(102,102,234,0.9) 0%, rgba(118,75,162,0.9) 70%)',
        backdropFilter: 'blur(10px)',
      }}
      open={isLoading}
    >
      <Paper
        elevation={16}
        sx={{
          p: 4,
          borderRadius: 3,
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          maxWidth: 300,
        }}
      >
        {/* Neural nodes */}
        <Box
          sx={{
            position: 'relative',
            width: 100,
            height: 100,
            mx: 'auto',
            mb: 3,
          }}
        >
          {[...Array(5)].map((_, i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                width: 12,
                height: 12,
                borderRadius: '50%',
                animation: `${neuralPulse} 2s infinite ease-in-out`,
                animationDelay: `${i * 0.4}s`,
                left: `${20 + (i % 3) * 30}%`,
                top: `${20 + Math.floor(i / 3) * 30}%`,
              }}
            />
          ))}
          
          {/* Central brain icon */}
          <Box
            sx={{
              position: 'absolute',
              left: '50%',
              top: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            <Psychology sx={{ fontSize: 32, color: 'white' }} />
          </Box>
        </Box>
        
        <Typography
          variant="h6"
          sx={{
            color: 'white',
            fontWeight: 500,
            mb: 1,
          }}
        >
          {message || 'Processing...'}
        </Typography>
        
        <Typography
          variant="body2"
          sx={{
            color: 'rgba(255,255,255,0.8)',
            fontStyle: 'italic',
          }}
        >
          Neural networks active
        </Typography>
      </Paper>
    </Backdrop>
  );
};

// Modern skeleton loader
export const SkeletonLoader = ({ isLoading }) => {
  if (!isLoading) return null;

  return (
    <Backdrop
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1000,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
      }}
      open={isLoading}
    >
      <Paper
        sx={{
          p: 4,
          borderRadius: 2,
          maxWidth: 400,
          width: '90%',
        }}
      >
        {/* Header skeleton */}
        <Box
          sx={{
            height: 40,
            borderRadius: 1,
            background: 'linear-gradient(90deg, #f0f0f0, #e0e0e0, #f0f0f0)',
            backgroundSize: '200% 100%',
            animation: `${waveLoading} 2s infinite ease-in-out`,
            mb: 2,
          }}
        />
        
        {/* Content skeletons */}
        {[...Array(3)].map((_, i) => (
          <Box
            key={i}
            sx={{
              height: 20,
              borderRadius: 1,
              background: 'linear-gradient(90deg, #f0f0f0, #e0e0e0, #f0f0f0)',
              backgroundSize: '200% 100%',
              animation: `${waveLoading} 2s infinite ease-in-out`,
              animationDelay: `${i * 0.2}s`,
              mb: 1.5,
              width: `${100 - (i * 10)}%`,
            }}
          />
        ))}
        
        <Typography
          variant="caption"
          sx={{
            display: 'block',
            textAlign: 'center',
            mt: 2,
            color: 'text.secondary',
            animation: `${skeletonPulse} 2s infinite`,
          }}
        >
          Loading your content...
        </Typography>
      </Paper>
    </Backdrop>
  );
};

// Progress wave loader
export const ProgressWaveLoader = ({ isLoading, message, progress = 0 }) => {
  const [animatedProgress, setAnimatedProgress] = useState(0);

  useEffect(() => {
    if (progress > animatedProgress) {
      const timer = setTimeout(() => {
        setAnimatedProgress(prev => Math.min(prev + 1, progress));
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [progress, animatedProgress]);

  if (!isLoading) return null;

  return (
    <Backdrop
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1000,
        background: 'linear-gradient(135deg, rgba(102,102,234,0.95) 0%, rgba(118,75,162,0.95) 100%)',
        backdropFilter: 'blur(12px)',
      }}
      open={isLoading}
    >
      <Paper
        elevation={20}
        sx={{
          p: 4,
          borderRadius: 4,
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.95)',
          maxWidth: 400,
          width: '90%',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Floating icon */}
        <Box
          sx={{
            animation: `${slideUp} 0.6s ease-out`,
            mb: 3,
          }}
        >
          <Lightbulb
            sx={{
              fontSize: 64,
              color: '#667eea',
              filter: 'drop-shadow(0 4px 12px rgba(102,102,234,0.3))',
            }}
          />
        </Box>
        
        <Typography
          variant="h5"
          sx={{
            mb: 2,
            fontWeight: 600,
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            animation: `${slideUp} 0.6s ease-out 0.2s both`,
          }}
        >
          {message || 'Loading...'}
        </Typography>
        
        {/* Progress bar */}
        <Box sx={{ width: '100%', mb: 2 }}>
          <LinearProgress
            variant="determinate"
            value={animatedProgress}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'rgba(102,102,234,0.1)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
                background: 'linear-gradient(90deg, #667eea, #764ba2, #f093fb)',
                backgroundSize: '200% 100%',
                animation: `${waveLoading} 2s infinite ease-in-out`,
              },
            }}
          />
        </Box>
        
        <Typography
          variant="body2"
          sx={{
            color: 'text.secondary',
            animation: `${slideUp} 0.6s ease-out 0.4s both`,
          }}
        >
          {animatedProgress}% complete
        </Typography>
      </Paper>
    </Backdrop>
  );
};

// Export a unified component that can switch between different loading types
const ModernLoadingVariants = ({ 
  isLoading, 
  message, 
  variant = 'neural', 
  progress = 0 
}) => {
  switch (variant) {
    case 'minimalist':
      return <MinimalistLoader isLoading={isLoading} message={message} />;
    case 'skeleton':
      return <SkeletonLoader isLoading={isLoading} />;
    case 'progress':
      return <ProgressWaveLoader isLoading={isLoading} message={message} progress={progress} />;
    case 'neural':
    default:
      return <NeuralNetworkLoader isLoading={isLoading} message={message} />;
  }
};

export default ModernLoadingVariants;
