import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  IconButton,
  CircularProgress,
  Alert,
  Fade,
  Zoom,
  useTheme,
} from '@mui/material';
import {
  FormatQuote,
  Refresh,
  Favorite,
  FavoriteBorder,
  Share,
  AutoAwesome,
} from '@mui/icons-material';

// Mock quotes data - replace with API call later
const QUOTES = [
  {
    id: 1,
    text: "The only way to do great work is to love what you do.",
    author: "Steve Jobs",
    category: "motivation"
  },
  {
    id: 2,
    text: "Learning never exhausts the mind.",
    author: "Leonardo da Vinci", 
    category: "learning"
  },
  {
    id: 3,
    text: "Education is the passport to the future, for tomorrow belongs to those who prepare for it today.",
    author: "Malcolm X",
    category: "education"
  },
  {
    id: 4,
    text: "The more that you read, the more things you will know. The more that you learn, the more places you'll go.",
    author: "Dr. Seuss",
    category: "reading"
  },
  {
    id: 5,
    text: "Success is not final, failure is not fatal: it is the courage to continue that counts.",
    author: "Winston Churchill",
    category: "perseverance"
  },
  {
    id: 6,
    text: "The future belongs to those who believe in the beauty of their dreams.",
    author: "Eleanor Roosevelt",
    category: "dreams"
  },
  {
    id: 7,
    text: "Intelligence is not the ability to store information, but to know where to find it.",
    author: "Albert Einstein",
    category: "wisdom"
  },
  {
    id: 8,
    text: "Don't let yesterday take up too much of today.",
    author: "Will Rogers",
    category: "focus"
  }
];

const DailyQuote = () => {
  const theme = useTheme();
  const [currentQuote, setCurrentQuote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isLiked, setIsLiked] = useState(false);
  const [fadeIn, setFadeIn] = useState(true);

  // Get quote based on current date to ensure same quote per day
  const getTodaysQuote = () => {
    const today = new Date();
    const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / 1000 / 60 / 60 / 24);
    return QUOTES[dayOfYear % QUOTES.length];
  };

  const loadQuote = async (refresh = false) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 800));
      
      let quote;
      if (refresh) {
        // Get random quote on refresh
        quote = QUOTES[Math.floor(Math.random() * QUOTES.length)];
      } else {
        // Get consistent daily quote
        quote = getTodaysQuote();
      }
      
      setCurrentQuote(quote);
      
      // Check if this quote was previously liked (simulate with localStorage)
      const likedQuotes = JSON.parse(localStorage.getItem('likedQuotes') || '[]');
      setIsLiked(likedQuotes.includes(quote.id));
      
    } catch (err) {
      setError('Failed to load daily quote. Please try again.');
      console.error('Error loading quote:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    setFadeIn(false);
    setTimeout(() => {
      loadQuote(true);
      setFadeIn(true);
    }, 200);
  };

  const handleLike = () => {
    if (!currentQuote) return;
    
    const likedQuotes = JSON.parse(localStorage.getItem('likedQuotes') || '[]');
    
    if (isLiked) {
      // Remove from liked
      const newLikedQuotes = likedQuotes.filter(id => id !== currentQuote.id);
      localStorage.setItem('likedQuotes', JSON.stringify(newLikedQuotes));
      setIsLiked(false);
    } else {
      // Add to liked
      const newLikedQuotes = [...likedQuotes, currentQuote.id];
      localStorage.setItem('likedQuotes', JSON.stringify(newLikedQuotes));
      setIsLiked(true);
    }
  };

  const handleShare = async () => {
    if (!currentQuote) return;
    
    const shareText = `"${currentQuote.text}" - ${currentQuote.author}`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Daily Quote',
          text: shareText,
        });
      } catch (err) {
        console.error('Error sharing:', err);
      }
    } else {
      // Fallback: copy to clipboard
      try {
        await navigator.clipboard.writeText(shareText);
        // You could show a snackbar here
      } catch (err) {
        console.error('Error copying to clipboard:', err);
      }
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      motivation: '#FF6B6B',
      learning: '#4ECDC4',
      education: '#45B7D1',
      reading: '#96CEB4',
      perseverance: '#FFEAA7',
      dreams: '#DDA0DD',
      wisdom: '#F39C12',
      focus: '#9B59B6'
    };
    return colors[category] || '#6C5CE7';
  };

  useEffect(() => {
    loadQuote();
  }, []);

  if (loading) {
    return (
      <Card 
        sx={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: 3,
          boxShadow: theme.shadows[8]
        }}
      >
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CircularProgress 
            size={32} 
            sx={{ color: 'white', mb: 2 }} 
          />
          <Typography variant="body2" sx={{ color: 'white' }}>
            Loading your daily inspiration...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card 
        sx={{ 
          borderRadius: 3,
          boxShadow: theme.shadows[4]
        }}
      >
        <CardContent>
          <Alert 
            severity="error" 
            action={
              <IconButton 
                size="small" 
                onClick={() => loadQuote()}
                sx={{ color: 'inherit' }}
              >
                <Refresh />
              </IconButton>
            }
          >
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!currentQuote) {
    return (
      <Card 
        sx={{ 
          borderRadius: 3,
          boxShadow: theme.shadows[4]
        }}
      >
        <CardContent sx={{ textAlign: 'center', py: 3 }}>
          <FormatQuote sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
          <Typography variant="body2" color="text.secondary">
            No quote available
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Fade in={fadeIn} timeout={500}>
      <Card 
        sx={{ 
          background: `linear-gradient(135deg, ${getCategoryColor(currentQuote.category)}15 0%, ${getCategoryColor(currentQuote.category)}08 100%)`,
          border: `1px solid ${getCategoryColor(currentQuote.category)}30`,
          borderRadius: 3,
          boxShadow: theme.shadows[6],
          position: 'relative',
          overflow: 'visible',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            background: `linear-gradient(90deg, ${getCategoryColor(currentQuote.category)} 0%, ${getCategoryColor(currentQuote.category)}80 100%)`,
            borderRadius: '12px 12px 0 0',
          }
        }}
      >
        {/* Header */}
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            px: 2,
            pt: 2,
            pb: 1
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AutoAwesome sx={{ color: getCategoryColor(currentQuote.category), fontSize: 20 }} />
            <Typography 
              variant="subtitle2" 
              sx={{ 
                color: getCategoryColor(currentQuote.category),
                fontWeight: 600,
                textTransform: 'uppercase',
                fontSize: '0.75rem',
                letterSpacing: 0.5
              }}
            >
              Daily Quote
            </Typography>
          </Box>
          
          <IconButton 
            size="small" 
            onClick={handleRefresh}
            sx={{
              color: 'text.secondary',
              '&:hover': { 
                backgroundColor: 'action.hover',
                transform: 'rotate(180deg)'
              },
              transition: 'transform 0.3s ease'
            }}
          >
            <Refresh fontSize="small" />
          </IconButton>
        </Box>

        <CardContent sx={{ pt: 0, pb: 2 }}>
          {/* Quote */}
          <Box sx={{ mb: 2, position: 'relative' }}>
            <FormatQuote 
              sx={{ 
                position: 'absolute',
                top: -8,
                left: -8,
                fontSize: 24,
                color: getCategoryColor(currentQuote.category),
                opacity: 0.3
              }} 
            />
            <Typography 
              variant="body1"
              sx={{ 
                fontStyle: 'italic',
                fontSize: '1rem',
                lineHeight: 1.6,
                color: 'text.primary',
                pl: 2,
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  left: 0,
                  top: 0,
                  bottom: 0,
                  width: 3,
                  background: getCategoryColor(currentQuote.category),
                  borderRadius: 2
                }
              }}
            >
              {currentQuote.text}
            </Typography>
          </Box>

          {/* Author */}
          <Typography 
            variant="body2" 
            sx={{ 
              textAlign: 'right',
              color: 'text.secondary',
              fontWeight: 500,
              mb: 2,
              fontStyle: 'normal'
            }}
          >
            — {currentQuote.author}
          </Typography>

          {/* Actions */}
          <Box 
            sx={{ 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              pt: 1,
              borderTop: '1px solid',
              borderColor: 'divider'
            }}
          >
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              <Zoom in={true} style={{ transitionDelay: '100ms' }}>
                <IconButton
                  size="small"
                  onClick={handleLike}
                  sx={{
                    color: isLiked ? '#e91e63' : 'text.secondary',
                    '&:hover': { 
                      color: '#e91e63',
                      backgroundColor: 'rgba(233, 30, 99, 0.08)'
                    }
                  }}
                >
                  {isLiked ? <Favorite fontSize="small" /> : <FavoriteBorder fontSize="small" />}
                </IconButton>
              </Zoom>
              
              <Zoom in={true} style={{ transitionDelay: '200ms' }}>
                <IconButton
                  size="small"
                  onClick={handleShare}
                  sx={{
                    color: 'text.secondary',
                    '&:hover': { 
                      color: 'primary.main',
                      backgroundColor: 'primary.light'
                    }
                  }}
                >
                  <Share fontSize="small" />
                </IconButton>
              </Zoom>
            </Box>

            <Typography 
              variant="caption" 
              sx={{ 
                color: 'text.secondary',
                textTransform: 'capitalize',
                fontSize: '0.7rem'
              }}
            >
              {currentQuote.category}
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Fade>
  );
};

export default DailyQuote;
