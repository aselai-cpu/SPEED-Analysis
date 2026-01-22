import React, { useState, useEffect, useRef } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import SendIcon from '@mui/icons-material/Send';
import CircularProgress from '@mui/material/CircularProgress';
import Paper from '@mui/material/Paper';
import { useQuery } from '../../hooks/useQuery';
import MessageCard from '../ResponseCard/MessageCard';

const ChatInterface = () => {
  const [input, setInput] = useState('');
  const { messages, sendQuery, isLoading } = useQuery();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Listen for example query events from sidebar
  useEffect(() => {
    const handleExampleQuery = (event) => {
      const query = event.detail;
      setInput(query);
      handleSend(query);
    };

    window.addEventListener('example-query', handleExampleQuery);
    return () => window.removeEventListener('example-query', handleExampleQuery);
  }, []);

  const handleSend = async (queryText = input) => {
    if (!queryText.trim() || isLoading) return;

    await sendQuery(queryText);
    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        flex: 1,
        height: '100%',
        bgcolor: 'background.default'
      }}
    >
      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
          gap: 2
        }}
      >
        {messages.length === 0 && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              color: 'text.secondary'
            }}
          >
            <Box sx={{ fontSize: 64, mb: 2 }}>🔍</Box>
            <Box sx={{ fontSize: 20, fontWeight: 500, mb: 1 }}>
              Ask a Question about Civil Unrest
            </Box>
            <Box sx={{ fontSize: 14, textAlign: 'center', maxWidth: 500 }}>
              Explore the SPEED Knowledge Graph using natural language.
              Ask about event patterns, actors, drivers, or temporal dynamics.
            </Box>
          </Box>
        )}

        {messages.map((message) => (
          <MessageCard key={message.id} message={message} />
        ))}

        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Paper
        elevation={3}
        sx={{
          p: 2,
          borderTop: 1,
          borderColor: 'divider'
        }}
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Ask about civil unrest patterns, actors, drivers, or temporal dynamics..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            variant="outlined"
            size="small"
          />
          <IconButton
            color="primary"
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            sx={{ alignSelf: 'flex-end' }}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatInterface;
