import { createTheme } from '@mui/material/styles';

// Emerald Green, Black, and White color palette
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#10b981', // Emerald Green
      light: '#34d399', // Light Emerald
      dark: '#059669', // Dark Emerald
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#000000', // Pure Black
      light: '#1f2937', // Dark Gray
      dark: '#000000',
      contrastText: '#ffffff',
    },
    success: {
      main: '#10b981', // Emerald Green
      light: '#34d399',
      dark: '#059669',
    },
    warning: {
      main: '#10b981', // Use Emerald for consistency
      light: '#34d399',
      dark: '#059669',
    },
    error: {
      main: '#000000', // Black for errors to maintain color scheme
      light: '#1f2937',
      dark: '#000000',
    },
    info: {
      main: '#10b981', // Emerald Green
      light: '#34d399',
      dark: '#059669',
    },
    background: {
      default: '#ffffff', // Pure White
      paper: '#ffffff', // Pure White
      secondary: '#f9fafb', // Very Light Gray
    },
    text: {
      primary: '#000000', // Pure Black
      secondary: '#1f2937', // Dark Gray
      disabled: '#6b7280', // Medium Gray
    },
    divider: '#e5e7eb', // Light Gray
    // Custom Emerald/Black/White gradients
    gradient: {
      primary: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', // Emerald gradient
      secondary: 'linear-gradient(135deg, #000000 0%, #1f2937 100%)', // Black gradient
      success: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)', // Emerald success
      ai: 'linear-gradient(135deg, #10b981 0%, #000000 100%)', // Emerald to Black
      learning: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', // Emerald learning
    },
  },
  typography: {
    fontFamily: [
      'Inter',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '3.5rem',
      fontWeight: 800,
      lineHeight: 1.2,
      letterSpacing: '-0.02em',
      background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
    h2: {
      fontSize: '2.75rem',
      fontWeight: 700,
      lineHeight: 1.3,
      letterSpacing: '-0.01em',
    },
    h3: {
      fontSize: '2.25rem',
      fontWeight: 700,
      lineHeight: 1.3,
    },
    h4: {
      fontSize: '1.875rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h6: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
    },
    button: {
      fontSize: '0.875rem',
      fontWeight: 500,
      textTransform: 'none',
      letterSpacing: '0.02em',
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0px 1px 3px rgba(0, 0, 0, 0.05)',
    '0px 4px 6px -1px rgba(0, 0, 0, 0.1)',
    '0px 10px 15px -3px rgba(0, 0, 0, 0.1)',
    '0px 20px 25px -5px rgba(0, 0, 0, 0.1)',
    '0px 25px 50px -12px rgba(0, 0, 0, 0.25)',
    // ... add more custom shadows
  ],
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          textTransform: 'none',
          fontWeight: 500,
          fontSize: '0.875rem',
          padding: '10px 24px',
          boxShadow: 'none',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0px 8px 25px rgba(0, 0, 0, 0.15)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
          },
        },
        outlined: {
          borderWidth: 2,
          '&:hover': {
            borderWidth: 2,
            backgroundColor: 'rgba(16, 185, 129, 0.04)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 4px 6px -1px rgba(0, 0, 0, 0.1)',
          border: '1px solid #e2e8f0',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-8px) scale(1.02)',
            boxShadow: '0px 25px 50px -12px rgba(0, 0, 0, 0.25)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 4px 6px -1px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#000000',
          backdropFilter: 'blur(12px)',
          color: '#ffffff',
          boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.15)',
          borderBottom: '1px solid rgba(16, 185, 129, 0.2)',
          borderRadius: 0, // Remove rounded corners
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: 'linear-gradient(180deg, #10b981 0%, #000000 100%)',
          borderRight: '1px solid #059669',
          boxShadow: '0px 4px 6px -1px rgba(0, 0, 0, 0.1)',
          color: 'white',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          margin: '4px 8px',
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            backgroundColor: 'rgba(16, 185, 129, 0.08)',
            transform: 'translateX(4px)',
          },
          '&.Mui-selected': {
            backgroundColor: 'rgba(16, 185, 129, 0.12)',
            borderLeft: '4px solid #10b981',
            '&:hover': {
              backgroundColor: 'rgba(16, 185, 129, 0.16)',
            },
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            transition: 'all 0.2s ease-in-out',
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#10b981',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderWidth: 2,
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
  },
});

// Add custom animations
theme.animations = {
  fadeIn: {
    '@keyframes fadeIn': {
      '0%': {
        opacity: 0,
        transform: 'translateY(10px)',
      },
      '100%': {
        opacity: 1,
        transform: 'translateY(0)',
      },
    },
    animation: 'fadeIn 0.3s ease-out',
  },
  slideIn: {
    '@keyframes slideIn': {
      '0%': {
        transform: 'translateX(-100%)',
      },
      '100%': {
        transform: 'translateX(0)',
      },
    },
    animation: 'slideIn 0.3s ease-out',
  },
  pulse: {
    '@keyframes pulse': {
      '0%': {
        transform: 'scale(1)',
      },
      '50%': {
        transform: 'scale(1.05)',
      },
      '100%': {
        transform: 'scale(1)',
      },
    },
    animation: 'pulse 2s infinite',
  },
};

export default theme;
