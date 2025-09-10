import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Alert,
  Button
} from '@mui/material';
import { CloudUpload, Assignment } from '@mui/icons-material';

const SummarizerTestPage = () => {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Container maxWidth="lg">
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Assignment sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          
          <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
            Document Summarizer
          </Typography>
          
          <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
            Routing is working correctly! This is the Document Summarizer page.
          </Typography>
          
          <Alert severity="success" sx={{ mb: 3 }}>
            Success! You've successfully navigated to the Summarizer page. 
            The routing configuration is working properly.
          </Alert>
          
          <Typography variant="body1" sx={{ mb: 4 }}>
            This is a test page to confirm that the routing is set up correctly.
            The full Document Summarizer functionality will be available once the backend is configured.
          </Typography>
          
          <Button
            variant="contained"
            size="large"
            startIcon={<CloudUpload />}
            sx={{ mr: 2 }}
          >
            Test Upload Button
          </Button>
          
          <Button
            variant="outlined"
            size="large"
          >
            Test Button
          </Button>
          
          <Box sx={{ mt: 4, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>
              What's Next?
            </Typography>
            <Typography variant="body2">
              1. Sidebar navigation - Added "Summarizer" option<br/>
              2. Routing configuration - Route "/summarizer" is working<br/>
              3. Backend setup - Install Python dependencies and run migrations<br/>
              4. Full UI - Replace this test page with DocumentSummarizerPage<br/>
            </Typography>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default SummarizerTestPage;
