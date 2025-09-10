import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  Divider,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
  Button,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard,
  Psychology,
  TrendingUp,
  Person,
  Logout,
  ChevronLeft,
  ChevronRight,
  AdminPanelSettings,
  NoteAdd,
  PlayLesson,
  Assignment,
  Note,
  School,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import NotificationDropdown from '../common/NotificationDropdown';

const drawerWidth = 280;
const collapsedDrawerWidth = 72;

const Layout = ({ children }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleDrawerCollapse = () => {
    setCollapsed(!collapsed);
  };

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Navigation items based on user role
  const getNavigationItems = () => {
    const baseItems = [
      { text: 'Dashboard', icon: Dashboard, path: '/dashboard' },
      { text: 'AI Tutor', icon: Psychology, path: '/chatbot' },
      { text: 'Notes', icon: Note, path: '/notes' },
      { text: 'Courses', icon: School, path: '/courses' },
      { text: 'Summarizer', icon: Assignment, path: '/summarizer' },
      { text: 'Progress', icon: TrendingUp, path: '/progress' },
    ];

    const adminItems = [
      ...baseItems,
      { text: 'Admin Panel', icon: AdminPanelSettings, path: '/admin/dashboard' },
    ];

    switch (user?.role) {
      case 'admin':
        return adminItems;
      default:
        return baseItems;
    }
  };

  const navigationItems = getNavigationItems();

  const drawer = (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        background: 'linear-gradient(180deg, #10b981 0%, #000000 100%)',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Logo and Header */}
      <Box
        sx={{
          p: collapsed ? 1 : 3,
          textAlign: 'center',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          transition: theme.transitions.create('padding'),
        }}
      >
        <Avatar
          sx={{
            width: collapsed ? 40 : 64,
            height: collapsed ? 40 : 64,
            mx: 'auto',
            mb: collapsed ? 1 : 2,
            background: 'rgba(255, 255, 255, 0.2)',
            transition: theme.transitions.create(['width', 'height']),
          }}
        >
          <Psychology fontSize="large" sx={{ color: '#ffffff' }} />
        </Avatar>
        {!collapsed && (
          <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
            TutorAI
          </Typography>
        )}
      </Box>

      {/* Navigation */}
      <List sx={{ flexGrow: 1, px: 1, py: 2, overflow: 'auto', maxHeight: 'calc(100vh - 200px)' }}>
        {navigationItems.map((item) => (
          <Tooltip
            key={item.text}
            title={collapsed ? item.text : ''}
            placement="right"
            arrow
          >
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
              sx={{
                mx: 1,
                mb: 1,
                minHeight: 48,
                color: 'rgba(255, 255, 255, 0.9)',
                borderRadius: 2,
                px: collapsed ? 1 : 2,
                justifyContent: collapsed ? 'center' : 'flex-start',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  transform: collapsed ? 'scale(1.05)' : 'translateX(4px)',
                },
                '&.Mui-selected': {
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  borderLeft: collapsed ? 'none' : '4px solid white',
                  border: collapsed ? '2px solid rgba(255, 255, 255, 0.5)' : 'none',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.25)',
                  },
                },
                transition: theme.transitions.create(['transform', 'background-color', 'border']),
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: collapsed ? 'auto' : 56,
                  width: collapsed ? '100%' : 'auto',
                  justifyContent: 'center',
                  color: 'inherit',
                  mr: collapsed ? 0 : 0,
                  px: collapsed ? 0 : 0,
                }}
              >
                <item.icon sx={{ fontSize: collapsed ? '1.5rem' : '1.5rem' }} />
              </ListItemIcon>
              {!collapsed && <ListItemText primary={item.text} />}
            </ListItemButton>
          </Tooltip>
        ))}
      </List>

      {/* User Profile */}
      <Box
        sx={{
          p: collapsed ? 1 : 2,
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        <Box
          display="flex"
          alignItems="center"
          sx={{
            p: 1,
            cursor: 'pointer',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
            },
          }}
          onClick={handleProfileMenuOpen}
        >
          <Avatar
            sx={{
              width: 40,
              height: 40,
              mr: collapsed ? 0 : 2,
              background: 'rgba(255, 255, 255, 0.2)',
            }}
          >
            {user?.firstName?.[0]}
          </Avatar>
          {!collapsed && (
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="subtitle2" sx={{ color: 'white' }}>
                {user?.firstName} {user?.lastName}
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                {user?.role}
              </Typography>
            </Box>
          )}
        </Box>
      </Box>

      {/* Collapse Button for Desktop */}
      {!isMobile && (
        <IconButton
          onClick={handleDrawerCollapse}
          sx={{
            position: 'absolute',
            right: -20,
            top: '50%',
            transform: 'translateY(-50%)',
            backgroundColor: 'white',
            boxShadow: 2,
            width: 36,
            height: 36,
            zIndex: 1201,
            '&:hover': {
              backgroundColor: '#f5f5f5',
            },
          }}
        >
          {collapsed ? <ChevronRight /> : <ChevronLeft />}
        </IconButton>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: theme.zIndex.drawer + 1,
          ml: { xs: 0, md: collapsed ? `${collapsedDrawerWidth}px` : `${drawerWidth}px` },
          width: { xs: '100%', md: `calc(100% - ${collapsed ? collapsedDrawerWidth : drawerWidth}px)` },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          backgroundColor: '#000000',
          borderRadius: 0,
          boxShadow: 'none',
          borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
        }}
      >
        <Toolbar sx={{ minHeight: '70px' }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ 
              color: 'white',
              fontWeight: 'bold',
              fontSize: '1.4rem'
            }}
          >
            TutorAI
          </Typography>

          {/* Spacer to push content to right */}
          <Box sx={{ flexGrow: 1 }} />

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <NotificationDropdown />

            <Avatar
              sx={{
                width: 40,
                height: 40,
                cursor: 'pointer',
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              }}
              onClick={handleProfileMenuOpen}
            >
              {user?.firstName?.[0]}
            </Avatar>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Drawer */}
      <Box
        component="nav"
        sx={{ 
          width: { xs: 0, md: collapsed ? collapsedDrawerWidth : drawerWidth }, 
          flexShrink: { md: 0 },
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
              border: 'none',
              borderRadius: 0,
              overflowX: 'hidden',
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: collapsed ? collapsedDrawerWidth : drawerWidth,
              border: 'none',
              borderRadius: 0,
              overflowX: 'hidden',
              transition: theme.transitions.create(['width'], {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        PaperProps={{
          sx: {
            mt: 1,
            minWidth: 200,
          },
        }}
      >
        <MenuItem onClick={() => navigate('/profile')}>
          <ListItemIcon>
            <Person fontSize="small" />
          </ListItemIcon>
          My Profile
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 0,
          mt: { xs: 7, sm: 8 },
          minHeight: 'calc(100vh - 64px)',
          backgroundColor: theme.palette.background.default,
          overflow: 'auto',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
