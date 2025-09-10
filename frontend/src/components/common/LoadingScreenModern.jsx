import React, { useState, useEffect } from 'react';
import {
  Typography,
  Backdrop,
  Paper,
  Box,
  keyframes,
} from '@mui/material';
import { Psychology, AutoAwesome, School, TipsAndUpdates } from '@mui/icons-material';
import { useLoading } from '../../contexts/LoadingContext';

// Keyframe animations
const pulseGlow = keyframes`
  0% { 
    transform: scale(1); 
    box-shadow: 0 0 20px rgba(102, 102, 234, 0.3);
  }
  50% { 
    transform: scale(1.05); 
    box-shadow: 0 0 40px rgba(102, 102, 234, 0.6);
  }
  100% { 
    transform: scale(1); 
    box-shadow: 0 0 20px rgba(102, 102, 234, 0.3);
  }
`;

const floatAnimation = keyframes`
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  25% { transform: translateY(-10px) rotate(2deg); }
  50% { transform: translateY(-5px) rotate(-2deg); }
  75% { transform: translateY(-8px) rotate(1deg); }
`;

const spinGlow = keyframes`
  0% { 
    transform: rotate(0deg) scale(1);
    filter: hue-rotate(0deg);
  }
  25% { 
    transform: rotate(90deg) scale(1.1);
    filter: hue-rotate(90deg);
  }
  50% { 
    transform: rotate(180deg) scale(1);
    filter: hue-rotate(180deg);
  }
  75% { 
    transform: rotate(270deg) scale(1.1);
    filter: hue-rotate(270deg);
  }
  100% { 
    transform: rotate(360deg) scale(1);
    filter: hue-rotate(360deg);
  }
`;

const particleFloat = keyframes`
  0% { 
    transform: translateY(0px) translateX(0px) scale(0.5); 
    opacity: 0;
  }
  50% { 
    transform: translateY(-30px) translateX(15px) scale(1); 
    opacity: 1;
  }
  100% { 
    transform: translateY(-60px) translateX(-10px) scale(0.3); 
    opacity: 0;
  }
`;

const dotPulse = keyframes`
  0%, 20% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.5); opacity: 0.7; }
  80%, 100% { transform: scale(1); opacity: 1; }
`;

// Modern loading messages with AI theme
const loadingMessages = [
  'Initializing AI systems...',
  'Processing your learning path...',
  'Analyzing study patterns...',
  'Optimizing content for you...',
  'Personalizing experience...',
  'Connecting neural networks...',
  'Preparing smart recommendations...',
  'Loading intelligent features...'
];

const ModernLoadingScreen = ({ variant = 'aiOrb' }) => {
  const { isLoading, loadingMessage } = useLoading();
  const [currentMessage, setCurrentMessage] = useState(loadingMessage || loadingMessages[0]);
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    if (!loadingMessage) {
      const interval = setInterval(() => {
        setMessageIndex((prev) => (prev + 1) % loadingMessages.length);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [loadingMessage]);

  useEffect(() => {
    if (!loadingMessage) {
      setCurrentMessage(loadingMessages[messageIndex]);
    }
  }, [messageIndex, loadingMessage]);

  if (!isLoading) return null;

  const renderAIOrb = () => (
    <Box
      sx={{
        position: 'relative',
        width: 120,
        height: 120,
        mx: 'auto',
        mb: 3,
      }}
    >
      {/* Main orb */}
      <Box
        sx={{
          width: '100%',
          height: '100%',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          animation: `${pulseGlow} 2s infinite ease-in-out`,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Psychology sx={{ fontSize: 48, color: 'white', zIndex: 2 }} />
        
        {/* Floating particles */}
        {[...Array(6)].map((_, i) => (
          <Box
            key={i}
            sx={{
              position: 'absolute',
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: 'rgba(255,255,255,0.8)',
              animation: `${particleFloat} 3s infinite ease-in-out`,
              animationDelay: `${i * 0.5}s`,
              left: `${20 + (i * 10)}%`,
              top: `${30 + (i % 3 * 20)}%`,
            }}
          />
        ))}
      </Box>
      
      {/* Outer ring */}
      <Box
        sx={{
          position: 'absolute',
          top: -10,
          left: -10,
          width: 140,
          height: 140,
          border: '3px solid rgba(102, 102, 234, 0.3)',
          borderRadius: '50%',
          animation: `${spinGlow} 4s linear infinite`,
        }}
      />
    </Box>
  );

  const renderFloatingIcons = () => (
    <Box
      sx={{
        position: 'relative',
        width: 100,
        height: 100,
        mx: 'auto',
        mb: 3,
      }}
    >
      {[
        { Icon: Psychology, delay: 0, x: 0, y: 0 },
        { Icon: AutoAwesome, delay: 1, x: 30, y: -20 },
        { Icon: School, delay: 2, x: -30, y: -20 },
        { Icon: TipsAndUpdates, delay: 1.5, x: 0, y: -40 },
      ].map(({ Icon, delay, x, y }, i) => (
        <Box
          key={i}
          sx={{
            position: 'absolute',
            left: '50%',
            top: '50%',
            transform: `translate(${x - 12}px, ${y - 12}px)`,
            animation: `${floatAnimation} 3s infinite ease-in-out`,
            animationDelay: `${delay}s`,
          }}
        >
          <Icon
            sx={{
              fontSize: i === 0 ? 48 : 24,
              color: i === 0 ? '#667eea' : '#764ba2',
              filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.2))',
            }}
          />
        </Box>
      ))}
    </Box>
  );

  const renderPulsingDots = () => (
    <Box
      sx={{
        display: 'flex',
        gap: 1.5,
        justifyContent: 'center',
        alignItems: 'center',
        mb: 3,
        height: 60,
      }}
    >
      {[...Array(4)].map((_, i) => (
        <Box
          key={i}
          sx={{
            width: 16,
            height: 16,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            animation: `${dotPulse} 1.5s infinite ease-in-out`,
            animationDelay: `${i * 0.3}s`,
          }}
        />
      ))}
    </Box>
  );

  const renderLoadingContent = () => {
    switch (variant) {
      case 'floatingIcons':
        return renderFloatingIcons();
      case 'pulsingDots':
        return renderPulsingDots();
      case 'aiOrb':
      default:
        return renderAIOrb();
    }
  };

  return (
    <Backdrop
      sx={{
        color: '#fff',
        zIndex: (theme) => theme.zIndex.drawer + 1000,
        background: 'linear-gradient(135deg, rgba(102, 102, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%)',
        backdropFilter: 'blur(15px)',
      }}
      open={isLoading}
    >
      <Paper
        elevation={24}
        sx={{
          p: 4,
          borderRadius: 4,
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.3)',
          maxWidth: 350,
          minWidth: 320,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            background: 'linear-gradient(90deg, #667eea, #764ba2, #f093fb)',
            backgroundSize: '200% 100%',
            animation: `${spinGlow} 3s linear infinite`,
          },
        }}
      >
        {renderLoadingContent()}
        
        <Typography
          variant="h5"
          sx={{
            mb: 2,
            color: 'text.primary',
            fontWeight: 700,
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          {currentMessage}
        </Typography>
        
        <Typography
          variant="body1"
          sx={{
            color: 'text.secondary',
            opacity: 0.8,
            fontStyle: 'italic',
            fontSize: '0.9rem',
          }}
        >
          Powered by AI • Personalized for you
        </Typography>

        {/* Progress indicator */}
        <Box
          sx={{
            mt: 3,
            height: 3,
            borderRadius: 1.5,
            background: 'rgba(102, 102, 234, 0.2)',
            overflow: 'hidden',
            position: 'relative',
          }}
        >
          <Box
            sx={{
              height: '100%',
              borderRadius: 1.5,
              background: 'linear-gradient(90deg, #667eea, #764ba2)',
              width: '30%',
              animation: `${spinGlow} 2s linear infinite`,
              transformOrigin: 'left',
            }}
          />
        </Box>
      </Paper>
    </Backdrop>
  );
};

export default ModernLoadingScreen;
