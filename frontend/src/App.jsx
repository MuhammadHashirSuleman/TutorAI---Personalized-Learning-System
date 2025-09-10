import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import theme from './theme';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LoadingProvider } from './contexts/LoadingContext';
import { ErrorProvider } from './contexts/ErrorContext';

// Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import CoursesPage from './pages/CoursesPage';
import ProgressPage from './pages/ProgressPage';
import AITutorPage from './pages/AITutorPage';
import AdminDashboard from './pages/AdminDashboard';
import NotesPage from './pages/NotesPage';
import DocumentSummarizerPage from './pages/DocumentSummarizerPage';
import ApiTest from './components/debug/ApiTest';
import MyProfile from './components/profile/MyProfile';
import LandingPage from './pages/LandingPage';

// Components
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoadingScreen from './components/common/LoadingScreen';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <ErrorProvider>
          <AuthProvider>
            <LoadingProvider>
              <Router>
              <div className="App">
                <Routes>
                  {/* Public Routes */}
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/debug" element={<ApiTest />} />
                  
                  {/* Protected Routes */}
                  <Route
                    path="/*"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <AppRoutes />
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                </Routes>
                
                <ToastContainer
                  position="top-right"
                  autoClose={5000}
                  hideProgressBar={false}
                  newestOnTop={false}
                  closeOnClick
                  rtl={false}
                  pauseOnFocusLoss
                  draggable
                  pauseOnHover
                />
                <LoadingScreen />
              </div>
              </Router>
            </LoadingProvider>
          </AuthProvider>
        </ErrorProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

function AppRoutes() {
  const { user } = useAuth();
  
  const getDefaultRoute = () => {
    if (user?.role === 'admin') return '/admin/dashboard';
    return '/dashboard'; // Students go to main dashboard
  };

  return (
    <Routes>
      {/* Default redirect for authenticated app root */}
      <Route path="/home" element={<Navigate to={getDefaultRoute()} replace />} />
      
      {/* Common Routes */}
      <Route path="/dashboard" element={<DashboardPage />} />
      
      {/* Feature routes */}
      <Route path="/courses" element={<CoursesPage />} />
      <Route path="/chatbot" element={<AITutorPage />} />
      <Route path="/notes" element={<NotesPage />} />
      <Route path="/summarizer" element={<DocumentSummarizerPage />} />
      <Route path="/assessments" element={<div>AI Assessments Coming Soon</div>} />
      <Route path="/progress" element={<ProgressPage />} />
      <Route path="/admin/dashboard" element={<AdminDashboard />} />
      <Route path="/profile" element={<MyProfile />} />
      
      {/* 404 Route */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;
