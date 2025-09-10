import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogActions,
  Button,
  TextField,
  Chip,
  Alert,
  Box,
  Typography,
  IconButton,
  Stack,
} from '@mui/material';
import {
  Save,
  Add,
  Close,
  BookmarkAdd,
  Chat,
} from '@mui/icons-material';
import apiService from '../../services/apiService';

const ChatSaver = ({ sessionId, onChatSaved, className = "" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [notes, setNotes] = useState('');
  const [tags, setTags] = useState([]);
  const [currentTag, setCurrentTag] = useState('');
  const [loading, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [messages, setMessages] = useState([]);

  // Load messages from localStorage when component mounts
  useEffect(() => {
    const savedMessages = localStorage.getItem(`conversation_${sessionId}`);
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        setMessages(parsedMessages);
      } catch (error) {
        console.error('Error parsing saved messages:', error);
      }
    }
  }, [sessionId]);

  const addTag = () => {
    if (currentTag.trim() && !tags.includes(currentTag.trim())) {
      setTags([...tags, currentTag.trim()]);
      setCurrentTag('');
    }
  };

  const removeTag = (tagToRemove) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleSave = async () => {
    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setSaving(true);
    setError('');

    try {
      // Refresh token before making request
      apiService.refreshTokenFromStorage();
      
      const response = await apiService.post('/users/features/chats/save/', {
        session_id: sessionId,
        title: title.trim(),
        tags,
        notes: notes.trim(),
        messages: messages
      });

      // Clear form
      setTitle('');
      setNotes('');
      setTags([]);
      setIsOpen(false);

      // Callback to parent
      if (onChatSaved) {
        onChatSaved(response.data.saved_chat);
      }

    } catch (err) {
      console.error('Error saving chat:', err);
      console.error('Error response:', err.response);
      console.error('Error message:', err.message);
      
      let errorMessage = 'Failed to save chat';
      if (err.response?.data) {
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.error) {
          errorMessage = err.response.data.error;
        } else if (err.response.data.detail) {
          errorMessage = err.response.data.detail;
        } else {
          errorMessage = JSON.stringify(err.response.data);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && e.target.name === 'tag') {
      e.preventDefault();
      addTag();
    }
  };

  return (
    <>
      <Button 
        variant="outlined" 
        size="small" 
        startIcon={<BookmarkAdd />}
        onClick={() => setIsOpen(true)}
        className={className}
        sx={{ gap: 1 }}
      >
        Save Chat
      </Button>
      
      <Dialog open={isOpen} onClose={() => setIsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <Chat />
            <Typography variant="h6">Save Chat Session</Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            {error && (
              <Alert severity="error">{error}</Alert>
            )}
            
            <TextField
              label="Title"
              placeholder="Enter a title for this chat..."
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              fullWidth
              error={!title.trim() && error}
            />
            
            <Box>
              <Typography variant="body2" sx={{ mb: 1, fontWeight: 500 }}>
                Tags
              </Typography>
              <Box display="flex" gap={1} sx={{ mb: 1 }}>
                <TextField
                  placeholder="Add a tag..."
                  value={currentTag}
                  onChange={(e) => setCurrentTag(e.target.value)}
                  onKeyPress={handleKeyPress}
                  size="small"
                  sx={{ flexGrow: 1 }}
                />
                <Button 
                  variant="outlined" 
                  onClick={addTag}
                  disabled={!currentTag.trim()}
                  size="small"
                >
                  <Add />
                </Button>
              </Box>
              
              {tags.length > 0 && (
                <Box display="flex" flexWrap="wrap" gap={0.5}>
                  {tags.map((tag, index) => (
                    <Chip
                      key={index}
                      label={tag}
                      size="small"
                      onDelete={() => removeTag(tag)}
                      deleteIcon={<Close />}
                      variant="outlined"
                    />
                  ))}
                </Box>
              )}
            </Box>
            
            <TextField
              label="Notes (optional)"
              placeholder="Add any notes about this chat session..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              multiline
              rows={3}
              fullWidth
            />
          </Stack>
        </DialogContent>
        
        <DialogActions>
          <Button 
            onClick={() => setIsOpen(false)}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSave} 
            disabled={loading || !title.trim()}
            variant="contained"
            startIcon={<Save />}
          >
            {loading ? 'Saving...' : 'Save Chat'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ChatSaver;
