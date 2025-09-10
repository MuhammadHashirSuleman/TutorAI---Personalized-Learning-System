import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  IconButton,
  Avatar,
  Chip,
  CircularProgress,
  Button,
  Grid,
  Alert,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Send,
  Psychology,
  Person,
  Clear,
  Lightbulb,
  Code,
  Science,
  Calculate,
  Business,
  Language,
  Palette,
  Settings,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import aiService from '../services/aiService';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ChatSaver from '../components/features/ChatSaver';

const AITutorPage = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState('checking');
  const [availableModels, setAvailableModels] = useState([]);
  const [currentModel, setCurrentModel] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [conversationId] = useState(Date.now().toString());
  const [settingsOpen, setSettingsOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize conversation
  useEffect(() => {
    const initializeChat = async () => {
      // Check API status and available models
      const status = await aiService.getApiStatus();
      setApiStatus(status.status);
      setAvailableModels(status.models || []);
      setCurrentModel(aiService.getCurrentModel());

      // Load conversation history
      const savedMessages = localStorage.getItem(`conversation_${conversationId}`);
      if (savedMessages) {
        setMessages(JSON.parse(savedMessages));
      } else {
        // Send initial greeting
        const welcomeMessage = {
          id: Date.now(),
          role: 'assistant',
          content: `Hello ${user?.firstName || 'there'}! I'm your AI Study Assistant. I'm here to help you learn, understand concepts, solve problems, and explore any academic topic you're curious about.\n\n**I can help you with:**\n- Mathematics and problem-solving\n- Programming and computer science\n- Sciences (Physics, Chemistry, Biology)\n- Languages and writing\n- Business and economics\n- Arts and creativity\n- And much more!\n\nWhat would you like to learn about today?`,
          timestamp: new Date().toISOString(),
        };
        setMessages([welcomeMessage]);
      }
    };

    initializeChat();
  }, [conversationId, user]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Save messages to localStorage
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`conversation_${conversationId}`, JSON.stringify(messages));
    }
  }, [messages, conversationId]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setShowSuggestions(false);

    try {
      // Prepare conversation context (last 10 messages)
      const context = messages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await aiService.sendMessage(
        userMessage.content,
        context,
        user
      );

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        success: response.success,
        usage: response.usage,
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'I apologize, but I\'m having trouble responding right now. Please try again in a moment.',
        timestamp: new Date().toISOString(),
        error: true,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    inputRef.current?.focus();
  };

  const clearConversation = () => {
    setMessages([]);
    localStorage.removeItem(`conversation_${conversationId}`);
    setShowSuggestions(true);
  };

  const suggestions = aiService.getSuggestedQuestions(user?.primarySubject || 'computer-science');

  const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';
    
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
        }}
      >
        {!isUser && (
          <Avatar
            sx={{
              bgcolor: 'primary.main',
              mr: 1,
              width: 36,
              height: 36,
            }}
          >
            <Psychology />
          </Avatar>
        )}
        
        <Paper
          elevation={1}
          sx={{
            p: 2,
            maxWidth: '80%',
            bgcolor: isUser ? 'primary.main' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary',
            borderRadius: 2,
            borderTopRightRadius: isUser ? 0.5 : 2,
            borderTopLeftRadius: isUser ? 2 : 0.5,
          }}
        >
          <Box sx={{ mb: 1 }}>
            <ReactMarkdown
              components={{
                code({node, inline, className, children, ...props}) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={oneDark}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                }
              }}
            >
              {message.content}
            </ReactMarkdown>
          </Box>
          
          <Typography variant="caption" sx={{ opacity: 0.7 }}>
            {new Date(message.timestamp).toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </Typography>
          
          {message.error && (
            <Chip 
              label="Error" 
              color="error" 
              size="small" 
              sx={{ ml: 1 }} 
            />
          )}
          
          {!message.success && message.role === 'assistant' && !message.error && (
            <Chip 
              label="Offline Mode" 
              color="warning" 
              size="small" 
              sx={{ ml: 1 }} 
            />
          )}
        </Paper>
        
        {isUser && (
          <Avatar
            sx={{
              bgcolor: 'secondary.main',
              ml: 1,
              width: 36,
              height: 36,
            }}
          >
            <Person />
          </Avatar>
        )}
      </Box>
    );
  };

  const ApiStatusIndicator = () => {
    const getSeverity = () => {
      if (apiStatus === 'connected') return 'success';
      if (apiStatus === 'partial') return 'info';
      return 'warning';
    };
    
    const getMessage = () => {
      if (apiStatus === 'connected') {
        return `AI Tutor is online with ${availableModels.join(' and ')}!`;
      } else if (apiStatus === 'partial') {
        return `AI Tutor partially available with ${availableModels.join(' and ')}.`;
      } else if (availableModels.length > 0) {
        return `AI Tutor configured for ${availableModels.join(' and ')} but connection issues detected.`;
      } else {
        return 'AI Tutor is running in offline mode. Please configure your API keys in the .env file.';
      }
    };
    
    return (
      <Alert severity={getSeverity()} sx={{ mb: 2 }}>
        {getMessage()}
        {currentModel && (
          <Typography variant="body2" sx={{ mt: 1, opacity: 0.8 }}>
            Currently using: {currentModel.name}
          </Typography>
        )}
      </Alert>
    );
  };

  return (
    <Box sx={{ flexGrow: 1, height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Container maxWidth="lg" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', py: 2 }}>
        {/* Header */}
        <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid item>
              <Box display="flex" alignItems="center">
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2, width: 48, height: 48 }}>
                  <Psychology />
                </Avatar>
                <Box>
                  <Typography variant="h5" fontWeight="bold">
                    AI Study Assistant
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Your personal AI tutor for {user?.primarySubject?.replace('-', ' ') || 'all subjects'}
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item>
              <Box display="flex" gap={1} alignItems="center">
                {/* Save Chat Button - only show if there are messages */}
                {messages.length > 1 && (
                  <ChatSaver 
                    sessionId={conversationId}
                    onChatSaved={(savedChat) => {
                      console.log('Chat saved:', savedChat);
                      // Could show a success snackbar here
                    }}
                  />
                )}
                <Tooltip title="Clear Conversation">
                  <IconButton onClick={clearConversation} color="error">
                    <Clear />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Settings">
                  <IconButton onClick={() => setSettingsOpen(true)}>
                    <Settings />
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* API Status */}
        <ApiStatusIndicator />

        {/* Chat Messages */}
        <Paper 
          elevation={2} 
          sx={{ 
            flexGrow: 1, 
            display: 'flex', 
            flexDirection: 'column',
            minHeight: 0,
          }}
        >
          <Box
            sx={{
              flexGrow: 1,
              overflowY: 'auto',
              p: 2,
              minHeight: 400,
            }}
          >
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            
            {isLoading && (
              <Box display="flex" justifyContent="flex-start" mb={2}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 1, width: 36, height: 36 }}>
                  <Psychology />
                </Avatar>
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    bgcolor: 'background.paper',
                    borderRadius: 2,
                    borderTopLeftRadius: 0.5,
                  }}
                >
                  <Box display="flex" alignItems="center" gap={1}>
                    <CircularProgress size={16} />
                    <Typography variant="body2">AI is thinking...</Typography>
                  </Box>
                </Paper>
              </Box>
            )}
            
            <div ref={messagesEndRef} />
          </Box>

          {/* Suggestions */}
          {showSuggestions && messages.length <= 1 && (
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Typography variant="subtitle2" gutterBottom color="text.secondary">
                <Lightbulb sx={{ fontSize: 16, mr: 1, verticalAlign: 'middle' }} />
                Try asking about:
              </Typography>
              <Grid container spacing={1}>
                {suggestions.slice(0, 6).map((suggestion, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Button
                      variant="outlined"
                      size="small"
                      fullWidth
                      onClick={() => handleSuggestionClick(suggestion)}
                      sx={{
                        textTransform: 'none',
                        justifyContent: 'flex-start',
                        textAlign: 'left',
                      }}
                    >
                      {suggestion}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Input Area */}
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
            <Box display="flex" gap={1} alignItems="flex-end">
              <TextField
                ref={inputRef}
                fullWidth
                multiline
                maxRows={4}
                placeholder="Ask me anything about your studies..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                variant="outlined"
              />
              <IconButton
                color="primary"
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                sx={{ p: 1.5 }}
              >
                {isLoading ? <CircularProgress size={24} /> : <Send />}
              </IconButton>
            </Box>
            
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Press Enter to send, Shift+Enter for new line
            </Typography>
          </Box>
        </Paper>
      </Container>

      {/* Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>AI Tutor Settings</DialogTitle>
        <DialogContent>
          <Typography variant="body2" paragraph>
            <strong>Current Configuration:</strong>
          </Typography>
          <Typography variant="body2">
            • Model: DeepSeek V3.1 Chat
          </Typography>
          <Typography variant="body2">
            • Subject Focus: {user?.primarySubject?.replace('-', ' ') || 'General'}
          </Typography>
          <Typography variant="body2">
            • Education Level: {user?.educationLevel || 'Not specified'}
          </Typography>
          <Typography variant="body2">
            • API Status: {apiStatus}
          </Typography>
          
          <Alert severity="info" sx={{ mt: 2 }}>
            The AI tutor adapts its responses based on your profile and learning preferences.
            Responses are generated using advanced language models to provide accurate educational support.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AITutorPage;
