import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Grid,
  Box,
  Alert,
  CircularProgress,
  Chip,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  TextField,
} from '@mui/material';
import {
  ChatBubbleOutline as MessageSquare,
  DeleteOutline as Trash,
  Edit as EditIcon,
  Visibility as Eye,
  Search,
  Close,
} from '@mui/icons-material';
import apiService from '../../services/apiService';

const SavedChatsHistory = () => {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedChat, setSelectedChat] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const loadChats = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Mock chat history data
      const mockChats = [
        {
          id: 1,
          title: 'Understanding React useEffect',
          created_at: '2024-12-08T14:20:00Z',
          tags: ['react', 'hooks', 'frontend'],
          preview: 'useEffect runs after render by default. You can control it with dependency arrays...'
        },
        {
          id: 2,
          title: 'SQL Joins Explained',
          created_at: '2024-12-07T09:15:00Z',
          tags: ['database', 'sql'],
          preview: 'There are four main types of joins: INNER, LEFT, RIGHT, and FULL OUTER...'
        },
        {
          id: 3,
          title: 'Machine Learning Basics',
          created_at: '2024-12-06T16:45:00Z',
          tags: ['ml', 'ai', 'data-science'],
          preview: 'Machine learning involves training models on data to make predictions...'
        }
      ];
      
      setChats(mockChats);
      
    } catch (err) {
      console.error('Error loading chats:', err);
      setError(err.message || 'Failed to load saved chats');
    } finally {
      setLoading(false);
    }
  };

  const deleteChat = async (chatId) => {
    try {
      // Simple confirm replacement for eslint rule
      const proceed = window.confirm('Are you sure you want to delete this chat?');
      if (!proceed) return;
      
      setChats(chats.filter(c => c.id !== chatId));
    } catch (err) {
      console.error('Error deleting chat:', err);
      setError('Failed to delete chat');
    }
  };

  const filteredChats = chats.filter(c => 
    c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  useEffect(() => {
    loadChats();
  }, []);

  if (loading) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography>Loading saved chats...</Typography>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardHeader 
          title={
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="h6">Saved Chats History</Typography>
              <Box display="flex" alignItems="center" gap={1}>
                <Search />
                <TextField 
                  size="small"
                  placeholder="Search by title or tag"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </Box>
            </Box>
          }
        />
      </Card>

      <Card>
        <CardContent>
          {filteredChats.length === 0 ? (
            <Typography color="text.secondary" textAlign="center">
              No saved chats found.
            </Typography>
          ) : (
            <List>
              {filteredChats.map((chat) => (
                <ListItem key={chat.id} alignItems="flex-start" secondaryAction={
                  <Box>
                    <Button size="small" onClick={() => { setSelectedChat(chat); setViewDialogOpen(true); }}>
                      View
                    </Button>
                    <IconButton color="error" onClick={() => deleteChat(chat.id)}>
                      <Trash />
                    </IconButton>
                  </Box>
                }>
                  <ListItemAvatar>
                    <Avatar>
                      <MessageSquare />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText 
                    primary={
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Typography variant="subtitle1" fontWeight="bold">
                          {chat.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(chat.created_at).toLocaleString()}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {chat.preview}
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {chat.tags.map(tag => (
                            <Chip key={tag} label={tag} size="small" />
                          ))}
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* View Chat Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedChat?.title}
          <IconButton onClick={() => setViewDialogOpen(false)} sx={{ position: 'absolute', right: 8, top: 8 }}>
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            {selectedChat?.preview}
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {selectedChat?.tags.map(tag => (
              <Chip key={tag} label={tag} size="small" />
            ))}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SavedChatsHistory;
