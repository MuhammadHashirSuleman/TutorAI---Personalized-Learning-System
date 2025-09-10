import React, { useState } from 'react';
import { Button, Box, Typography, Alert } from '@mui/material';

const ApiTest = () => {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testBasicFetch = async () => {
    setLoading(true);
    setResult('Testing basic fetch...\n');
    
    try {
      console.log('🔍 Testing direct fetch to backend...');
      
      const testUrl = 'http://localhost:8000/api/auth/register/';
      console.log('🎯 Target URL:', testUrl);
      
      const testData = {
        username: 'debugtest123',
        email: 'debugtest123@example.com',
        password: 'testpass123',
        password_confirm: 'testpass123',
        first_name: 'Debug',
        last_name: 'Test',
        role: 'student'
      };
      
      console.log('📤 Sending data:', testData);
      
      const response = await fetch(testUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testData),
      });
      
      console.log('📥 Response received:', response);
      console.log('📊 Response status:', response.status);
      console.log('📋 Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Error response body:', errorText);
        setResult(prev => prev + `❌ HTTP ${response.status}: ${errorText}\n`);
      } else {
        const data = await response.json();
        console.log('✅ Success response:', data);
        setResult(prev => prev + `✅ Registration successful!\n${JSON.stringify(data, null, 2)}\n`);
      }
      
    } catch (error) {
      console.error('🚫 Fetch error:', error);
      setResult(prev => prev + `🚫 Network Error: ${error.message}\n`);
      
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        setResult(prev => prev + `💡 This is likely a CORS or connection issue\n`);
      }
    } finally {
      setLoading(false);
    }
  };

  const testAPIService = async () => {
    setLoading(true);
    setResult('Testing API Service...\n');
    
    try {
      // Import and test the API service
      const apiService = (await import('../../services/apiService')).default;
      
      console.log('🔧 Testing API Service...');
      console.log('🌐 API Service baseURL:', apiService.baseURL);
      
      const testData = {
        username: 'servicetest123',
        email: 'servicetest123@example.com',
        password: 'testpass123',
        password_confirm: 'testpass123',
        first_name: 'Service',
        last_name: 'Test',
        role: 'student'
      };
      
      const response = await apiService.register(testData);
      console.log('✅ API Service success:', response);
      setResult(prev => prev + `✅ API Service worked!\n${JSON.stringify(response, null, 2)}\n`);
      
    } catch (error) {
      console.error('❌ API Service error:', error);
      setResult(prev => prev + `❌ API Service Error: ${error.message}\n`);
    } finally {
      setLoading(false);
    }
  };

  const testTeacherRegistration = async () => {
    setLoading(true);
    setResult('Testing Teacher Registration...\n');
    
    try {
      // Import and test the API service with teacher role
      const apiService = (await import('../../services/apiService')).default;
      
      console.log('🧪 Testing teacher registration specifically...');
      
      const teacherData = {
        username: `teacher${Date.now()}`,
        email: `teacher${Date.now()}@example.com`,
        password: 'testpass123',
        password_confirm: 'testpass123',
        first_name: 'Test',
        last_name: 'Teacher',
        role: 'teacher'
      };
      
      console.log('📤 Teacher data:', teacherData);
      
      const response = await apiService.register(teacherData);
      console.log('✅ Teacher registration success:', response);
      setResult(prev => prev + `✅ Teacher registration worked!\n${JSON.stringify(response, null, 2)}\n`);
      
    } catch (error) {
      console.error('❌ Teacher registration error:', error);
      setResult(prev => prev + `❌ Teacher Registration Error: ${error.message}\n`);
      setResult(prev => prev + `Stack: ${error.stack}\n`);
    } finally {
      setLoading(false);
    }
  };

  const testCurrentEnv = () => {
    setResult('Environment Variables:\n');
    setResult(prev => prev + `REACT_APP_API_URL: ${process.env.REACT_APP_API_URL}\n`);
    setResult(prev => prev + `NODE_ENV: ${process.env.NODE_ENV}\n`);
    setResult(prev => prev + `Current origin: ${window.location.origin}\n`);
    
    console.log('🌍 Environment check:', {
      REACT_APP_API_URL: process.env.REACT_APP_API_URL,
      NODE_ENV: process.env.NODE_ENV,
      origin: window.location.origin
    });
  };

  return (
    <Box sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        🔧 API Debug Tool
      </Typography>
      
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button 
          variant="contained" 
          onClick={testBasicFetch}
          disabled={loading}
        >
          Test Direct Fetch
        </Button>
        <Button 
          variant="contained" 
          onClick={testAPIService}
          disabled={loading}
        >
          Test API Service
        </Button>
        <Button 
          variant="contained" 
          onClick={testTeacherRegistration}
          disabled={loading}
          color="warning"
        >
          Test Teacher Reg
        </Button>
        <Button 
          variant="outlined" 
          onClick={testCurrentEnv}
        >
          Check Environment
        </Button>
      </Box>

      {result && (
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography component="pre" sx={{ whiteSpace: 'pre-wrap', fontSize: '0.8rem' }}>
            {result}
          </Typography>
        </Alert>
      )}
      
      <Typography variant="body2" color="text.secondary">
        Open browser console (F12) for detailed logs
      </Typography>
    </Box>
  );
};

export default ApiTest;
