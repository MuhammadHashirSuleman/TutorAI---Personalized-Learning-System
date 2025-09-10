import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  IconButton,
  Rating,
  InputAdornment,
  Tabs,
  Tab,
  Pagination,
  Skeleton,
} from '@mui/material';
import {
  Search,
  School,
  AccessTime,
  People,
  OpenInNew,
  BookmarkBorder,
  Bookmark,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  getCoursesByField, 
  getAllCourses, 
  searchCourses,
  getRecommendedCourses 
} from '../data/courses';
import recommendationService from '../services/recommendationService';
import RedirectAnimation from '../components/common/RedirectAnimation';

const CoursesPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [selectedProvider, setSelectedProvider] = useState('all');
  const [currentTab, setCurrentTab] = useState(0);
  const [bookmarkedCourses, setBookmarkedCourses] = useState(new Set());
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [redirectAnimation, setRedirectAnimation] = useState({
    open: false,
    courseTitle: '',
    provider: '',
    destinationUrl: ''
  });
  const coursesPerPage = 9;

  const categories = [
    { value: 'all', label: 'All Courses' },
    { value: 'computer-science', label: 'Computer Science' },
    { value: 'mathematics', label: 'Mathematics' },
    { value: 'science', label: 'Science' },
    { value: 'business', label: 'Business' },
    { value: 'languages', label: 'Languages' },
    { value: 'arts', label: 'Arts & Humanities' },
  ];

  const levels = [
    { value: 'all', label: 'All Levels' },
    { value: 'Beginner', label: 'Beginner' },
    { value: 'Intermediate', label: 'Intermediate' },
    { value: 'Advanced', label: 'Advanced' },
  ];

  const providers = [
    { value: 'all', label: 'All Providers' },
    { value: 'Coursera', label: 'Coursera' },
    { value: 'Udemy', label: 'Udemy' },
    { value: 'NVIDIA', label: 'NVIDIA' },
    { value: 'Microsoft', label: 'Microsoft' },
    { value: 'LinkedIn Learning', label: 'LinkedIn Learning' },
  ];

  const filterCourses = useCallback(async () => {
    let filtered = courses;

    // Filter by tab
    if (currentTab === 1) {
      // AI-powered recommended courses
      filtered = await recommendationService.getCourseRecommendations(courses, 12);
    } else if (currentTab === 2) {
      // Bookmarked courses
      filtered = courses.filter(course => bookmarkedCourses.has(course.id));
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = getCoursesByField(selectedCategory);
      if (currentTab === 2) {
        filtered = filtered.filter(course => bookmarkedCourses.has(course.id));
      }
    }

    // Filter by search query
    if (searchQuery) {
      filtered = searchCourses(searchQuery);
      // Track search query for AI recommendations
      recommendationService.trackSearchQuery(searchQuery);
      if (selectedCategory !== 'all') {
        filtered = filtered.filter(course => {
          const fieldCourses = getCoursesByField(selectedCategory);
          return fieldCourses.some(fc => fc.id === course.id);
        });
      }
      if (currentTab === 2) {
        filtered = filtered.filter(course => bookmarkedCourses.has(course.id));
      }
    }

    // Filter by level
    if (selectedLevel !== 'all') {
      filtered = filtered.filter(course => course.level.includes(selectedLevel));
    }

    // Filter by provider
    if (selectedProvider !== 'all') {
      filtered = filtered.filter(course => course.provider === selectedProvider);
    }

    setFilteredCourses(filtered);
    setPage(1);
  }, [courses, currentTab, user?.primarySubject, bookmarkedCourses, selectedCategory, searchQuery, selectedLevel, selectedProvider]);

  useEffect(() => {
    // Simulate loading
    setLoading(true);
    setTimeout(() => {
      const allCourses = getAllCourses();
      setCourses(allCourses);
      setFilteredCourses(allCourses);
      setLoading(false);
    }, 1000);

    // Load bookmarked courses from localStorage
    const saved = localStorage.getItem('bookmarkedCourses');
    if (saved) {
      setBookmarkedCourses(new Set(JSON.parse(saved)));
    }
  }, []);

  useEffect(() => {
    const applyFilters = async () => {
      await filterCourses();
    };
    applyFilters();
  }, [filterCourses]);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const toggleBookmark = (courseId) => {
    const newBookmarked = new Set(bookmarkedCourses);
    const isBookmarking = !newBookmarked.has(courseId);
    
    if (newBookmarked.has(courseId)) {
      newBookmarked.delete(courseId);
    } else {
      newBookmarked.add(courseId);
    }
    
    setBookmarkedCourses(newBookmarked);
    localStorage.setItem('bookmarkedCourses', JSON.stringify([...newBookmarked]));
    
    // Track bookmark action for AI recommendations
    recommendationService.trackBookmark(courseId, isBookmarking);
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const paginatedCourses = filteredCourses.slice(
    (page - 1) * coursesPerPage,
    page * coursesPerPage
  );

  // Handle course redirect with animation
  const handleCourseRedirect = (course) => {
    console.log('CoursesPage: handleCourseRedirect called with course:', course);
    console.log('CoursesPage: Course URL:', course.url);
    
    // Track course click for AI recommendations
    recommendationService.trackCourseClick(course.id);
    recommendationService.trackCourseView(course.id, {
      subject: course.category,
      difficulty: course.level,
      provider: course.provider
    });

    // Show redirect animation
    setRedirectAnimation({
      open: true,
      courseTitle: course.title,
      provider: course.provider,
      destinationUrl: course.url
    });
    
    console.log('CoursesPage: Set redirectAnimation state to:', {
      open: true,
      courseTitle: course.title,
      provider: course.provider,
      destinationUrl: course.url
    });
  };

  const handleRedirectComplete = (url) => {
    console.log('CoursesPage: handleRedirectComplete called with URL:', url);
    try {
      window.open(url, '_blank');
      console.log('CoursesPage: Successfully opened URL in new tab');
    } catch (error) {
      console.error('CoursesPage: Error opening URL:', error);
    }
  };

  const CourseCard = ({ course }) => (
    <Card 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: (theme) => theme.shadows[8],
        },
        // Ensure consistent card heights
        minHeight: 480,
      }}
    >
      <CardMedia
        component="img"
        height="200"
        image={course.thumbnail}
        alt={course.title}
        sx={{ objectFit: 'cover' }}
      />
      <CardContent 
        sx={{ 
          flexGrow: 1, 
          p: 2, 
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          minHeight: 280, // Ensure consistent content height
        }}
      >
        <Box sx={{ flexGrow: 1 }}>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
            <Typography variant="h6" component="h3" sx={{ 
              fontWeight: 600, 
              lineHeight: 1.2,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
          }}>
            {course.title}
          </Typography>
          <IconButton
            size="small"
            onClick={() => toggleBookmark(course.id)}
            sx={{ ml: 1, flexShrink: 0 }}
          >
            {bookmarkedCourses.has(course.id) ? (
              <Bookmark color="primary" />
            ) : (
              <BookmarkBorder />
            )}
          </IconButton>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
          by {course.instructor}
        </Typography>

        <Typography 
          variant="body2" 
          sx={{ 
            mb: 2,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical',
          }}
        >
          {course.description}
        </Typography>

        <Box display="flex" alignItems="center" mb={2}>
          <Rating value={course.rating} precision={0.1} size="small" readOnly />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            {course.rating} ({(course.students / 1000).toFixed(0)}k students)
          </Typography>
        </Box>

        <Box display="flex" gap={1} mb={2} flexWrap="wrap">
          <Chip label={course.level} size="small" color="primary" variant="outlined" />
          <Chip label={course.provider} size="small" variant="outlined" />
          <Chip 
            label="FREE" 
            size="small" 
            color="success" 
            sx={{ fontWeight: 'bold' }}
          />
        </Box>

        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center">
            <AccessTime sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {course.duration}
            </Typography>
          </Box>
          <Box display="flex" alignItems="center">
            <People sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {(course.students / 1000).toFixed(0)}k
            </Typography>
          </Box>
        </Box>

        <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
          {course.topics.slice(0, 3).map((topic, index) => (
            <Chip 
              key={index}
              label={topic} 
              size="small" 
              variant="outlined"
              sx={{ fontSize: '0.7rem' }}
            />
          ))}
          {course.topics.length > 3 && (
            <Chip 
              label={`+${course.topics.length - 3} more`}
              size="small" 
              variant="outlined"
              sx={{ fontSize: '0.7rem' }}
            />
          )}
        </Box>
        </Box>
        
        {/* Button positioned at bottom */}
        <Box sx={{ mt: 'auto', pt: 1 }}>
          <Button
            variant="contained"
            fullWidth
            startIcon={<OpenInNew />}
            onClick={() => handleCourseRedirect(course)}
            sx={{ 
              py: 1.5,
              borderRadius: 2,
              textTransform: 'none',
              fontWeight: 600,
              fontSize: '0.95rem'
            }}
          >
            Start Learning
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  const LoadingSkeleton = () => (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Skeleton variant="rectangular" height={200} />
      <CardContent sx={{ flexGrow: 1, p: 2 }}>
        <Skeleton variant="text" height={32} sx={{ mb: 1 }} />
        <Skeleton variant="text" height={20} sx={{ mb: 1.5 }} />
        <Skeleton variant="text" height={60} sx={{ mb: 2 }} />
        <Box display="flex" gap={1} mb={2}>
          <Skeleton variant="rounded" width={60} height={24} />
          <Skeleton variant="rounded" width={80} height={24} />
          <Skeleton variant="rounded" width={40} height={24} />
        </Box>
        <Skeleton variant="rectangular" height={36} />
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ flexGrow: 1, py: 3 }}>
      <Container maxWidth="xl">
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
            External Courses
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Self-paced courses from top platforms like Udemy, Coursera, NVIDIA, Microsoft, and LinkedIn Learning
          </Typography>
          <Box sx={{ 
            mt: 2, 
            p: 2,
            backgroundColor: 'info.50',
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'info.200'
          }}>
            <Typography variant="body2" color="info.main" sx={{ fontWeight: 500 }}>
              💡 Looking for teacher-led classes with personalized guidance? 
              <Button 
                variant="text" 
                size="small" 
                onClick={() => navigate('/classes')}
                sx={{ ml: 1, textTransform: 'none' }}
              >
                Check out Classes →
              </Button>
            </Typography>
          </Box>
        </Box>

        {/* Tabs */}
        <Box sx={{ mb: 3 }}>
          <Tabs value={currentTab} onChange={handleTabChange}>
            <Tab label="All Courses" />
            <Tab label="Recommended" />
            <Tab label="Bookmarked" />
          </Tabs>
        </Box>

        {/* Filters */}
        <Box sx={{ mb: 4 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search courses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} sm={4} md={2}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  label="Category"
                >
                  {categories.map((category) => (
                    <MenuItem key={category.value} value={category.value}>
                      {category.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4} md={2}>
              <FormControl fullWidth>
                <InputLabel>Level</InputLabel>
                <Select
                  value={selectedLevel}
                  onChange={(e) => setSelectedLevel(e.target.value)}
                  label="Level"
                >
                  {levels.map((level) => (
                    <MenuItem key={level.value} value={level.value}>
                      {level.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4} md={2}>
              <FormControl fullWidth>
                <InputLabel>Provider</InputLabel>
                <Select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  label="Provider"
                >
                  {providers.map((provider) => (
                    <MenuItem key={provider.value} value={provider.value}>
                      {provider.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Typography variant="body2" color="text.secondary">
                {filteredCourses.length} courses found
              </Typography>
            </Grid>
          </Grid>
        </Box>

        {/* Course Grid */}
        {loading ? (
          <Grid container spacing={3}>
            {Array.from(new Array(9)).map((_, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <LoadingSkeleton />
              </Grid>
            ))}
          </Grid>
        ) : (
          <>
            <Grid container spacing={3}>
              {paginatedCourses.map((course) => (
                <Grid item xs={12} sm={6} md={4} key={course.id}>
                  <CourseCard course={course} />
                </Grid>
              ))}
            </Grid>

            {filteredCourses.length === 0 && !loading && (
              <Box textAlign="center" py={8}>
                <School sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  No courses found
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Try adjusting your filters or search terms
                </Typography>
              </Box>
            )}

            {/* Pagination */}
            {filteredCourses.length > coursesPerPage && (
              <Box display="flex" justifyContent="center" mt={4}>
                <Pagination
                  count={Math.ceil(filteredCourses.length / coursesPerPage)}
                  page={page}
                  onChange={handlePageChange}
                  color="primary"
                  size="large"
                />
              </Box>
            )}
          </>
        )}
      </Container>
      
      {/* Redirect Animation Modal */}
      <RedirectAnimation
        open={redirectAnimation.open}
        courseTitle={redirectAnimation.courseTitle}
        provider={redirectAnimation.provider}
        destinationUrl={redirectAnimation.destinationUrl}
        onRedirect={handleRedirectComplete}
        onClose={() => setRedirectAnimation({ open: false, courseTitle: '', provider: '', destinationUrl: '' })}
      />
    </Box>
  );
};

export default CoursesPage;
