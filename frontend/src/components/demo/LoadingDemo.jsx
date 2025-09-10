import React, { useState } from 'react';
import {
  Container,
  Typography,
  Button,
  Stack,
  Paper,
  Grid,
  Box,
  Chip,
} from '@mui/material';
import { PlayArrow, Stop } from '@mui/icons-material';

// Import all our modern loading components
import ModernLoadingScreen from '../common/LoadingScreenModern';
import ModernLoadingVariants, {
  MinimalistLoader,
  NeuralNetworkLoader,
  SkeletonLoader,
  ProgressWaveLoader,
} from '../common/LoadingAnimations';

const LoadingDemo = () => {
  const [activeLoader, setActiveLoader] = useState(null);
  const [progress, setProgress] = useState(0);

  const startLoader = (loaderType) => {
    setActiveLoader(loaderType);
    
    // For progress loader, simulate progress
    if (loaderType === 'progress') {
      setProgress(0);
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 10;
        });
      }, 300);
    }
  };

  const stopLoader = () => {
    setActiveLoader(null);
    setProgress(0);
  };

  const loaderOptions = [
    {
      name: 'AI Orb (Original Enhanced)',
      type: 'aiOrb',
      description: 'Pulsing AI orb with floating particles and rotating ring',
      component: ModernLoadingScreen,
      props: { variant: 'aiOrb' }
    },
    {
      name: 'Floating Icons',
      type: 'floatingIcons',
      description: 'Educational icons floating around a central brain icon',
      component: ModernLoadingScreen,
      props: { variant: 'floatingIcons' }
    },
    {
      name: 'Pulsing Dots',
      type: 'pulsingDots',
      description: 'Modern minimalist dots with sequential pulsing animation',
      component: ModernLoadingScreen,
      props: { variant: 'pulsingDots' }
    },
    {
      name: 'Neural Network',
      type: 'neural',
      description: 'AI-themed with neural node animations',
      component: NeuralNetworkLoader,
      props: {}
    },
    {
      name: 'Minimalist Morph',
      type: 'minimalist',
      description: 'Clean morphing shape with breathing animation',
      component: MinimalistLoader,
      props: {}
    },
    {
      name: 'Skeleton Loader',
      type: 'skeleton',
      description: 'Modern skeleton loading for content areas',
      component: SkeletonLoader,
      props: {}
    },
    {
      name: 'Progress Wave',
      type: 'progress',
      description: 'Animated progress bar with wave effects',
      component: ProgressWaveLoader,
      props: { progress }
    }
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Modern Loading Animations Demo
      </Typography>
      
      <Typography variant="h6" color="text.secondary" align="center" sx={{ mb: 4 }}>
        Choose from various modern, engaging loading animations for your AI Study platform
      </Typography>

      <Grid container spacing={3}>
        {loaderOptions.map((loader) => (
          <Grid item xs={12} sm={6} md={4} key={loader.type}>
            <Paper
              elevation={3}
              sx={{
                p: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'all 0.3s ease',
                '&:hover': {
                  elevation: 8,
                  transform: 'translateY(-4px)',
                },
              }}
            >
              <Typography variant="h6" component="h3" gutterBottom>
                {loader.name}
              </Typography>
              
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 2, flexGrow: 1 }}
              >
                {loader.description}
              </Typography>

              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={loader.type === 'progress' ? 'Interactive Progress' : 'Pure Animation'} 
                  size="small"
                  color={loader.type === 'progress' ? 'primary' : 'secondary'}
                  variant="outlined"
                />
              </Box>

              <Stack direction="row" spacing={1}>
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={() => startLoader(loader.type)}
                  disabled={activeLoader === loader.type}
                  size="small"
                  fullWidth
                >
                  Preview
                </Button>
              </Stack>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* Control Panel */}
      {activeLoader && (
        <Paper
          elevation={4}
          sx={{
            position: 'fixed',
            bottom: 20,
            right: 20,
            p: 2,
            minWidth: 200,
            zIndex: 1300,
          }}
        >
          <Typography variant="subtitle1" gutterBottom>
            Currently showing: <strong>{activeLoader}</strong>
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Stop />}
            onClick={stopLoader}
            fullWidth
            color="error"
          >
            Stop Preview
          </Button>
        </Paper>
      )}

      {/* Render active loader */}
      {activeLoader && (() => {
        const activeLoaderConfig = loaderOptions.find(l => l.type === activeLoader);
        const LoaderComponent = activeLoaderConfig.component;
        
        return (
          <LoaderComponent
            isLoading={true}
            message="Demo loading message"
            {...activeLoaderConfig.props}
          />
        );
      })()}

      {/* Implementation Instructions */}
      <Paper sx={{ p: 3, mt: 4, bgcolor: 'grey.50' }}>
        <Typography variant="h5" gutterBottom>
          How to implement:
        </Typography>
        
        <Typography variant="body1" paragraph>
          1. <strong>Replace your current LoadingScreen:</strong> Simply replace the import in your components from the old LoadingScreen to one of these modern versions.
        </Typography>
        
        <Typography variant="body1" paragraph>
          2. <strong>Use with your existing LoadingContext:</strong> All these components work with your existing `useLoading()` hook and context.
        </Typography>
        
        <Typography variant="body1" paragraph>
          3. <strong>Choose your favorite:</strong> Pick the animation style that best fits your AI Study platform's brand and user experience.
        </Typography>

        <Box sx={{ mt: 2, p: 2, bgcolor: 'primary.50', borderRadius: 1 }}>
          <Typography variant="h6" color="primary" gutterBottom>
            💡 Recommendation:
          </Typography>
          <Typography variant="body2">
            For an AI Study platform, I recommend the <strong>"AI Orb"</strong> or <strong>"Neural Network"</strong> 
            variants as they best represent the intelligent, educational nature of your application while providing 
            engaging visual feedback to users.
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default LoadingDemo;
