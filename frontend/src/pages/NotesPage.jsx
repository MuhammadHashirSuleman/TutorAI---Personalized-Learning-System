import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Chip,
  InputAdornment,
  Fab,
  Alert,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Add,
  Search,
  Edit,
  Delete,
  Save,
  Cancel,
  MoreVert,
  Note,
  FilterList,
  SortByAlpha,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/apiService';

const NotesPage = () => {
  const { user } = useAuth();
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('updated_at');
  const [filterBy, setFilterBy] = useState('all');
  const [selectedNote, setSelectedNote] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [noteToDelete, setNoteToDelete] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);

  const [noteForm, setNoteForm] = useState({
    title: '',
    content: '',
    subject: '',
    tags: [],
  });

  const subjects = [
    'Mathematics',
    'Physics',
    'Chemistry',
    'Biology',
    'Computer Science',
    'English',
    'History',
    'Geography',
    'Economics',
    'Business',
    'Arts',
    'Music',
    'General',
  ];

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      setLoading(true);
      const data = await apiService.getNotes();
      setNotes(data.results || data);
    } catch (error) {
      console.error('Failed to fetch notes:', error);
      setError('Failed to load notes. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateNote = () => {
    setNoteForm({ title: '', content: '', subject: '', tags: [] });
    setSelectedNote(null);
    setIsEditing(false);
    setDialogOpen(true);
  };

  const handleEditNote = (note) => {
    setNoteForm({
      title: note.title,
      content: note.content,
      subject: note.subject || '',
      tags: note.tags || [],
    });
    setSelectedNote(note);
    setIsEditing(true);
    setDialogOpen(true);
    setAnchorEl(null);
  };

  const handleSaveNote = async () => {
    try {
      if (!noteForm.title.trim() || !noteForm.content.trim()) {
        setError('Title and content are required');
        return;
      }

      const noteData = {
        title: noteForm.title.trim(),
        content: noteForm.content.trim(),
        subject: noteForm.subject,
        tags: noteForm.tags,
      };

      if (isEditing && selectedNote) {
        await apiService.updateNote(selectedNote.id, noteData);
        setNotes(notes.map(note => 
          note.id === selectedNote.id 
            ? { ...note, ...noteData, updated_at: new Date().toISOString() }
            : note
        ));
      } else {
        const newNote = await apiService.createNote(noteData);
        setNotes([newNote, ...notes]);
      }

      setDialogOpen(false);
      setError('');
    } catch (error) {
      console.error('Failed to save note:', error);
      setError('Failed to save note. Please try again.');
    }
  };

  const handleDeleteNote = (note) => {
    setNoteToDelete(note);
    setDeleteConfirmOpen(true);
    setAnchorEl(null);
  };

  const confirmDeleteNote = async () => {
    try {
      if (noteToDelete) {
        await apiService.deleteNote(noteToDelete.id);
        setNotes(notes.filter(note => note.id !== noteToDelete.id));
        setDeleteConfirmOpen(false);
        setNoteToDelete(null);
      }
    } catch (error) {
      console.error('Failed to delete note:', error);
      setError('Failed to delete note. Please try again.');
    }
  };

  const handleFormChange = (field, value) => {
    setNoteForm({ ...noteForm, [field]: value });
  };

  const handleTagAdd = (tag) => {
    if (tag && !noteForm.tags.includes(tag)) {
      setNoteForm({ ...noteForm, tags: [...noteForm.tags, tag] });
    }
  };

  const handleTagRemove = (tagToRemove) => {
    setNoteForm({
      ...noteForm,
      tags: noteForm.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const filteredNotes = notes
    .filter(note => {
      const matchesSearch = 
        note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        note.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (note.tags && note.tags.some(tag => 
          tag.toLowerCase().includes(searchQuery.toLowerCase())
        ));
      
      const matchesFilter = filterBy === 'all' || 
        note.subject === filterBy;
      
      return matchesSearch && matchesFilter;
    })
    .sort((a, b) => {
      if (sortBy === 'title') {
        return a.title.localeCompare(b.title);
      } else if (sortBy === 'created_at') {
        return new Date(b.created_at) - new Date(a.created_at);
      } else {
        return new Date(b.updated_at) - new Date(a.updated_at);
      }
    });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <Box sx={{ flexGrow: 1, p: 3 }}>
        <Container maxWidth="lg">
          <Typography variant="h4" gutterBottom>Loading notes...</Typography>
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
            My Notes
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Create, organize, and manage your personal study notes
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Search and Filters */}
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search notes..."
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
            <Grid item xs={12} sm={4} md={3}>
              <TextField
                select
                fullWidth
                label="Subject"
                value={filterBy}
                onChange={(e) => setFilterBy(e.target.value)}
              >
                <MenuItem value="all">All Subjects</MenuItem>
                {subjects.map((subject) => (
                  <MenuItem key={subject} value={subject}>
                    {subject}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4} md={2}>
              <TextField
                select
                fullWidth
                label="Sort by"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="updated_at">Last Updated</MenuItem>
                <MenuItem value="created_at">Created Date</MenuItem>
                <MenuItem value="title">Title (A-Z)</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} md={1}>
              <Typography variant="body2" color="text.secondary">
                {filteredNotes.length} notes
              </Typography>
            </Grid>
          </Grid>
        </Box>

        {/* Notes Grid */}
        {filteredNotes.length === 0 ? (
          <Box textAlign="center" py={8}>
            <Note sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              {searchQuery || filterBy !== 'all' ? 'No notes found' : 'No notes yet'}
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              {searchQuery || filterBy !== 'all' 
                ? 'Try adjusting your search or filters'
                : 'Create your first note to get started with organized studying'
              }
            </Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={handleCreateNote}
              size="large"
            >
              Create Your First Note
            </Button>
          </Box>
        ) : (
          <Grid container spacing={3}>
            {filteredNotes.map((note) => (
              <Grid item xs={12} sm={6} md={4} key={note.id}>
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
                    <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                      <Typography variant="h6" component="h3" sx={{ 
                        fontWeight: 600,
                        lineHeight: 1.2,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        flexGrow: 1,
                        mr: 1,
                      }}>
                        {note.title}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={(e) => setAnchorEl({ element: e.currentTarget, note })}
                      >
                        <MoreVert />
                      </IconButton>
                    </Box>

                    <Typography 
                      variant="body2" 
                      color="text.secondary"
                      sx={{ 
                        mb: 2,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 4,
                        WebkitBoxOrient: 'vertical',
                        minHeight: '4em',
                      }}
                    >
                      {note.content}
                    </Typography>

                    <Box display="flex" gap={1} mb={2} flexWrap="wrap">
                      {note.subject && (
                        <Chip label={note.subject} size="small" color="primary" variant="outlined" />
                      )}
                      {note.tags && note.tags.slice(0, 2).map((tag, index) => (
                        <Chip key={index} label={tag} size="small" variant="outlined" />
                      ))}
                      {note.tags && note.tags.length > 2 && (
                        <Chip label={`+${note.tags.length - 2} more`} size="small" variant="outlined" />
                      )}
                    </Box>

                    <Typography variant="caption" color="text.secondary">
                      Updated {formatDate(note.updated_at)}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Floating Action Button */}
        <Fab
          color="primary"
          aria-label="add note"
          onClick={handleCreateNote}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
          }}
        >
          <Add />
        </Fab>

        {/* Note Menu */}
        <Menu
          anchorEl={anchorEl?.element}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
        >
          <MenuItem onClick={() => handleEditNote(anchorEl?.note)}>
            <ListItemIcon>
              <Edit fontSize="small" />
            </ListItemIcon>
            <ListItemText>Edit</ListItemText>
          </MenuItem>
          <MenuItem onClick={() => handleDeleteNote(anchorEl?.note)}>
            <ListItemIcon>
              <Delete fontSize="small" />
            </ListItemIcon>
            <ListItemText>Delete</ListItemText>
          </MenuItem>
        </Menu>

        {/* Note Dialog */}
        <Dialog
          open={dialogOpen}
          onClose={() => setDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            {isEditing ? 'Edit Note' : 'Create New Note'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 1 }}>
              <TextField
                fullWidth
                label="Note Title"
                value={noteForm.title}
                onChange={(e) => handleFormChange('title', e.target.value)}
                sx={{ mb: 2 }}
              />
              
              <TextField
                select
                fullWidth
                label="Subject"
                value={noteForm.subject}
                onChange={(e) => handleFormChange('subject', e.target.value)}
                sx={{ mb: 2 }}
              >
                <MenuItem value="">None</MenuItem>
                {subjects.map((subject) => (
                  <MenuItem key={subject} value={subject}>
                    {subject}
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                fullWidth
                multiline
                rows={12}
                label="Note Content"
                value={noteForm.content}
                onChange={(e) => handleFormChange('content', e.target.value)}
                placeholder="Write your note content here..."
                sx={{ mb: 2 }}
              />

              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Tags
                </Typography>
                <Box display="flex" gap={1} flexWrap="wrap" mb={1}>
                  {noteForm.tags.map((tag, index) => (
                    <Chip
                      key={index}
                      label={tag}
                      size="small"
                      onDelete={() => handleTagRemove(tag)}
                    />
                  ))}
                </Box>
                <TextField
                  size="small"
                  placeholder="Add tags (press Enter)"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && e.target.value.trim()) {
                      handleTagAdd(e.target.value.trim());
                      e.target.value = '';
                    }
                  }}
                />
              </Box>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)} startIcon={<Cancel />}>
              Cancel
            </Button>
            <Button onClick={handleSaveNote} variant="contained" startIcon={<Save />}>
              {isEditing ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Confirmation Dialog */}
        <Dialog
          open={deleteConfirmOpen}
          onClose={() => setDeleteConfirmOpen(false)}
        >
          <DialogTitle>Delete Note</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete "{noteToDelete?.title}"? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDeleteConfirmOpen(false)}>
              Cancel
            </Button>
            <Button onClick={confirmDeleteNote} color="error" variant="contained">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default NotesPage;
