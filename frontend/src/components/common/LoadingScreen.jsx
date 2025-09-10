import React, { useState, useEffect } from 'react';
import {
  Typography,
  Backdrop,
  Paper,
  Box,
  CircularProgress,
  keyframes,
} from '@mui/material';
 import { School, Psychology, AutoAwesome } from '@mui/icons-material';
import { useLoading } from '../../contexts/LoadingContext';

// Clean, modern animations
const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const gentlePulse = keyframes`
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.02);
  }
`;

const smoothRotate = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

// Clean loading messages
const loadingMessages = [
  'Signing you in...',
  'Almost there...',
  'Setting up your dashboard...',
  'Loading your profile...'
];

const LoadingScreen = () => {
  const { isLoading, loadingMessage } = useLoading();
  const [currentMessage, setCurrentMessage] = useState(loadingMessage || loadingMessages[0]);
  const [messageIndex, setMessageIndex] = useState(0);

  // Cycle through loading messages if no custom message provided
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
    } else {
      setCurrentMessage(loadingMessage);
    }
  }, [messageIndex, loadingMessage]);

  if (!isLoading) return null;

  return (
    <Backdrop
      sx={{
        color: '#fff',
        zIndex: (theme) => theme.zIndex.drawer + 1000,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(12px)',
      }}
      open={isLoading}
    >
      <Paper
        elevation={16}
        sx={{
          p: 4,
          borderRadius: 3,
          textAlign: 'center',
          background: 'rgba(255, 255, 255, 0.98)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          maxWidth: 320,
          minWidth: 280,
          position: 'relative',
          animation: `${fadeIn} 0.4s ease-out`,
        }}
      >
        {/* Clean loading icon */}
        <Box
          sx={{
            position: 'relative',
            width: 80,
            height: 80,
            mx: 'auto',
            mb: 3,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <CircularProgress
            size={60}
            thickness={3}
            sx={{
              color: '#667eea',
              position: 'absolute',
              animation: `${smoothRotate} 1.5s linear infinite`,
            }}
          />
          <School
            sx={{
              fontSize: 32,
              color: '#667eea',
              animation: `${gentlePulse} 2s ease-in-out infinite`,
            }}
          />
        </Box>
        
        <Typography
          variant="h6"
          sx={{
            mb: 1,
            color: 'text.primary',
            fontWeight: 600,
          }}
        >
          {currentMessage}
        </Typography>
        
        <Typography
          variant="body2"
          sx={{
            color: 'text.secondary',
            opacity: 0.7,
            fontSize: '0.875rem',
          }}
        >
          Please wait a moment...
        </Typography>
      </Paper>
    </Backdrop>
  );
};

export default LoadingScreen;
