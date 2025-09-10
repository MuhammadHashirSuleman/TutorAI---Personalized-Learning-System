import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  LinearProgress,
  Tabs,
  Tab,
  Paper,
  Divider,
  InputAdornment,
} from '@mui/material';
import {
  CloudUpload,
  PictureAsPdf,
  Description,
  Favorite,
  FavoriteBorder,
  MoreVert,
  Delete,
  Edit,
  Visibility,
  Search,
  FilterList,
  FileDownload,
  Refresh,
  Analytics,
  Assignment,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useLoading } from '../contexts/LoadingContext';
import apiService from '../services/apiService';
import { formatDate, formatFileSize } from '../utils/helpers';

const DocumentSummarizerPage = () => {
  const { user } = useAuth();
  const { showLoading, hideLoading } = useLoading();
  
  // State management
  const [documents, setDocuments] = useState([]);
  const [loading, setLocalLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploadDialog, setUploadDialog] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Filters and search
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [fileTypeFilter, setFileTypeFilter] = useState('all');
  const [showFavorites, setShowFavorites] = useState(false);
  
  // Dialog states
  const [viewDialog, setViewDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  
  // Upload form
  const [uploadForm, setUploadForm] = useState({
    title: '',
    subject: '',
    tags: [],
    notes: '',
    file: null
  });
  
  // Dashboard stats
  const [dashboardStats, setDashboardStats] = useState(null);
  
  useEffect(() => {
    fetchDocuments();
    fetchDashboard();
  }, []);
  
  const fetchDocuments = async () => {
    try {
      setLocalLoading(true);
      const params = new URLSearchParams();
      
      if (searchQuery) params.append('query', searchQuery);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (fileTypeFilter !== 'all') params.append('file_type', fileTypeFilter);
      if (showFavorites) params.append('is_favorite', 'true');
      
      const response = await apiService.get(`/users/features/documents/?${params}`);
      console.log('Documents API response:', response);
      
      // Handle both paginated and non-paginated responses
      if (response && response.results) {
        // Paginated response
        setDocuments(response.results);
      } else if (response && Array.isArray(response)) {
        // Direct array response
        setDocuments(response);
      } else {
        // Fallback to empty array
        console.warn('Unexpected response format:', response);
        setDocuments([]);
      }
      setError('');
    } catch (error) {
      console.error('Failed to fetch documents:', error);
      setError(error.message || 'Failed to load documents. Please try again.');
      setDocuments([]); // Set empty array on error
    } finally {
      setLocalLoading(false);
    }
  };
  
  const fetchDashboard = async () => {
    try {
      const response = await apiService.get('/users/features/documents/dashboard/');
      console.log('Dashboard API response:', response);
      setDashboardStats(response);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
      // Set fallback dashboard stats
      setDashboardStats({
        statistics: {
          total_documents: 0,
          success_rate: 0,
          pdf_count: 0,
          docx_count: 0
        }
      });
    }
  };
  
  const handleFileUpload = async () => {
    if (!uploadForm.file) {
      setError('Please select a file to upload');
      return;
    }
    
    try {
      showLoading('Uploading and processing document...');
      setUploadProgress(0);
      
      const formData = new FormData();
      formData.append('file', uploadForm.file);
      formData.append('title', uploadForm.title);
      formData.append('subject', uploadForm.subject);
      formData.append('notes', uploadForm.notes);
      formData.append('tags', JSON.stringify(uploadForm.tags));
      
      const response = await apiService.post('/users/features/documents/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });
      
      console.log('Upload API response:', response);
      
      // Check if upload was successful - response is the data directly, not wrapped in .data
      if (response && (response.success || response.status === 'success' || response.id)) {
        setUploadDialog(false);
        setUploadForm({ title: '', subject: '', tags: [], notes: '', file: null });
        setUploadProgress(0);
        fetchDocuments();
        fetchDashboard();
        setError('');
      } else {
        setError(response?.message || response?.error || 'Upload failed');
      }
      
    } catch (error) {
      console.error('Upload failed:', error);
      setError(error.message || 'Upload failed');
    } finally {
      hideLoading();
      setUploadProgress(0);
    }
  };
  
  const handleDeleteDocument = async (documentId) => {
    try {
      await apiService.delete(`/users/features/documents/${documentId}/`);
      setDocuments(docs => docs.filter(doc => doc.id !== documentId));
      fetchDashboard();
      setAnchorEl(null);
    } catch (error) {
      console.error('Delete failed:', error);
      setError('Failed to delete document');
    }
  };
  
  const handleToggleFavorite = async (documentId) => {
    try {
      await apiService.post(`/users/features/documents/${documentId}/toggle-favorite/`);
      setDocuments(docs => docs.map(doc => 
        doc.id === documentId ? { ...doc, is_favorite: !doc.is_favorite } : doc
      ));
      setAnchorEl(null);
    } catch (error) {
      console.error('Toggle favorite failed:', error);
      setError('Failed to update favorite status');
    }
  };
  
  const handleViewDocument = async (document) => {
    try {
      const response = await apiService.get(`/users/features/documents/${document.id}/`);
      setSelectedDocument(response);
      setViewDialog(true);
    } catch (error) {
      console.error('Failed to load document details:', error);
      setError('Failed to load document details');
    }
  };
  
  const getFileIcon = (fileType) => {
    return fileType === 'pdf' ? <PictureAsPdf color="error" /> : <Description color="primary" />;
  };
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };
  
  const filteredDocuments = documents.filter(doc => {
    if (tabValue === 1 && !doc.is_favorite) return false;
    if (tabValue === 2 && doc.status !== 'failed') return false;
    return true;
  });
  
  if (loading) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Container maxWidth="lg">
          <Typography variant="h4" gutterBottom>Loading documents...</Typography>
        </Container>
      </Box>
    );
  }
  
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Container maxWidth="lg">
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
            Document Summarizer
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Upload PDF and DOCX files to generate AI-powered summaries
          </Typography>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}
        
        {/* Dashboard Stats */}
        {dashboardStats && (
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <Assignment sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{dashboardStats.statistics.total_documents}</Typography>
                      <Typography variant="body2" color="text.secondary">Total Documents</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <Analytics sx={{ fontSize: 40, color: 'success.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{dashboardStats.statistics.success_rate}%</Typography>
                      <Typography variant="body2" color="text.secondary">Success Rate</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <PictureAsPdf sx={{ fontSize: 40, color: 'error.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{dashboardStats.statistics.pdf_count}</Typography>
                      <Typography variant="body2" color="text.secondary">PDF Files</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center">
                    <Description sx={{ fontSize: 40, color: 'info.main', mr: 2 }} />
                    <Box>
                      <Typography variant="h4">{dashboardStats.statistics.docx_count}</Typography>
                      <Typography variant="body2" color="text.secondary">DOCX Files</Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
        
        {/* Controls */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search documents..."
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
              <TextField
                select
                fullWidth
                size="small"
                label="Status"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <MenuItem value="all">All Status</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="processing">Processing</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4} md={2}>
              <TextField
                select
                fullWidth
                size="small"
                label="File Type"
                value={fileTypeFilter}
                onChange={(e) => setFileTypeFilter(e.target.value)}
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
                <MenuItem value="docx">DOCX</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Button
                fullWidth
                variant="outlined"
                onClick={fetchDocuments}
                startIcon={<Search />}
              >
                Search
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Button
                fullWidth
                variant="contained"
                onClick={() => setUploadDialog(true)}
                startIcon={<CloudUpload />}
              >
                Upload
              </Button>
            </Grid>
          </Grid>
        </Paper>
        
        {/* Tabs */}
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
          <Tab label="All Documents" />
          <Tab label="Favorites" />
          <Tab label="Failed" />
        </Tabs>
        
        {/* Documents Grid */}
        {filteredDocuments.length === 0 ? (
          <Box textAlign="center" py={8}>
            <CloudUpload sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              {tabValue === 0 ? 'No documents yet' : tabValue === 1 ? 'No favorite documents' : 'No failed documents'}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              {tabValue === 0 ? 'Upload your first PDF or DOCX file to get started' : 
               tabValue === 1 ? 'Mark documents as favorite to see them here' : 
               'All your documents processed successfully'}
            </Typography>
            {tabValue === 0 && (
              <Button
                variant="contained"
                startIcon={<CloudUpload />}
                onClick={() => setUploadDialog(true)}
                size="large"
              >
                Upload Document
              </Button>
            )}
          </Box>
        ) : (
          <Grid container spacing={3}>
            {filteredDocuments.map((document) => (
              <Grid item xs={12} sm={6} md={4} key={document.id}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: (theme) => theme.shadows[4],
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                      <Box display="flex" alignItems="center">
                        {getFileIcon(document.file_type)}
                        <Box ml={1}>
                          <Typography variant="h6" component="h3" sx={{ 
                            fontWeight: 600,
                            lineHeight: 1.2,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                          }}>
                            {document.title || document.original_filename}
                          </Typography>
                        </Box>
                      </Box>
                      <Box>
                        {document.is_favorite && <Favorite color="error" sx={{ mr: 1 }} />}
                        <IconButton
                          size="small"
                          onClick={(e) => setAnchorEl({ element: e.currentTarget, document })}
                        >
                          <MoreVert />
                        </IconButton>
                      </Box>
                    </Box>
                    
                    <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                      <Chip 
                        label={document.status} 
                        size="small" 
                        color={getStatusColor(document.status)}
                        variant="outlined"
                      />
                      <Chip 
                        label={document.file_type.toUpperCase()} 
                        size="small" 
                        variant="outlined"
                      />
                      {document.subject && (
                        <Chip label={document.subject} size="small" color="primary" variant="outlined" />
                      )}
                    </Box>
                    
                    {document.status === 'completed' && (
                      <Box mb={2}>
                        <Typography variant="body2" color="text.secondary">
                          {document.word_count} words → {document.summary_word_count} words 
                          ({document.compression_ratio}% compression)
                        </Typography>
                      </Box>
                    )}
                    
                    <Typography variant="caption" color="text.secondary">
                      {document.file_size_display} • Uploaded {formatDate(document.created_at)}
                    </Typography>
                    
                    {document.status === 'processing' && (
                      <Box mt={2}>
                        <LinearProgress />
                      </Box>
                    )}
                  </CardContent>
                  
                  {document.status === 'completed' && (
                    <Box p={2} pt={0}>
                      <Button
                        fullWidth
                        variant="contained"
                        onClick={() => handleViewDocument(document)}
                        startIcon={<Visibility />}
                      >
                        View Summary
                      </Button>
                    </Box>
                  )}
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
        
        {/* Document Menu */}
        <Menu
          anchorEl={anchorEl?.element}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
        >
          {anchorEl?.document.status === 'completed' && (
            <MenuItem onClick={() => handleViewDocument(anchorEl.document)}>
              <ListItemIcon>
                <Visibility fontSize="small" />
              </ListItemIcon>
              <ListItemText>View Summary</ListItemText>
            </MenuItem>
          )}
          <MenuItem onClick={() => handleToggleFavorite(anchorEl?.document.id)}>
            <ListItemIcon>
              {anchorEl?.document.is_favorite ? 
                <FavoriteBorder fontSize="small" /> : 
                <Favorite fontSize="small" />
              }
            </ListItemIcon>
            <ListItemText>
              {anchorEl?.document.is_favorite ? 'Remove from Favorites' : 'Add to Favorites'}
            </ListItemText>
          </MenuItem>
          <MenuItem onClick={() => handleDeleteDocument(anchorEl?.document.id)}>
            <ListItemIcon>
              <Delete fontSize="small" />
            </ListItemIcon>
            <ListItemText>Delete</ListItemText>
          </MenuItem>
        </Menu>
        
        {/* Upload Dialog */}
        <Dialog
          open={uploadDialog}
          onClose={() => setUploadDialog(false)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Upload Document</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 1 }}>
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => setUploadForm({...uploadForm, file: e.target.files[0]})}
                style={{ display: 'none' }}
                id="file-upload"
              />
              <label htmlFor="file-upload">
                <Button
                  variant="outlined"
                  component="span"
                  fullWidth
                  sx={{ mb: 2, py: 2 }}
                  startIcon={<CloudUpload />}
                >
                  {uploadForm.file ? uploadForm.file.name : 'Choose PDF or DOCX file'}
                </Button>
              </label>
              
              <TextField
                fullWidth
                label="Title (optional)"
                value={uploadForm.title}
                onChange={(e) => setUploadForm({...uploadForm, title: e.target.value})}
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Subject (optional)"
                value={uploadForm.subject}
                onChange={(e) => setUploadForm({...uploadForm, subject: e.target.value})}
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Notes (optional)"
                value={uploadForm.notes}
                onChange={(e) => setUploadForm({...uploadForm, notes: e.target.value})}
                placeholder="Add any notes about this document..."
              />
              
              {uploadProgress > 0 && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress variant="determinate" value={uploadProgress} />
                  <Typography variant="caption" color="text.secondary">
                    {uploadProgress}% uploaded
                  </Typography>
                </Box>
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setUploadDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleFileUpload}
              variant="contained"
              disabled={!uploadForm.file || uploadProgress > 0}
            >
              Upload & Process
            </Button>
          </DialogActions>
        </Dialog>
        
        {/* View Document Dialog */}
        <Dialog
          open={viewDialog}
          onClose={() => setViewDialog(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            {selectedDocument?.title || selectedDocument?.original_filename}
          </DialogTitle>
          <DialogContent>
            {selectedDocument && (
              <Box>
                <Box display="flex" gap={1} mb={3}>
                  <Chip label={selectedDocument.file_type.toUpperCase()} size="small" />
                  <Chip label={selectedDocument.file_size_display} size="small" variant="outlined" />
                  {selectedDocument.subject && (
                    <Chip label={selectedDocument.subject} size="small" color="primary" />
                  )}
                </Box>
                
                <Typography variant="h6" gutterBottom>
                  AI-Generated Summary
                </Typography>
                <Paper sx={{ p: 2, mb: 3, bgcolor: 'primary.50', border: '1px solid', borderColor: 'primary.200' }}>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
                    {selectedDocument.summary}
                  </Typography>
                </Paper>
                
                {selectedDocument.summary_metadata && (
                  <Box mb={3}>
                    <Typography variant="body2" color="text.secondary">
                      Summary generated using {selectedDocument.summary_metadata.summary_info?.method || 'AI'} • 
                      {selectedDocument.word_count} words compressed to {selectedDocument.summary_word_count} words 
                      ({selectedDocument.compression_ratio}% of original)
                    </Typography>
                  </Box>
                )}
                
                {selectedDocument.notes && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      Notes
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedDocument.notes}
                    </Typography>
                  </Box>
                )}
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setViewDialog(false)}>
              Close
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default DocumentSummarizerPage;
