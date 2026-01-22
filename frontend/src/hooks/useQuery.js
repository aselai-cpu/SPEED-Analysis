import { useState, useCallback } from 'react';
import apiService from '../services/apiService';

export const useQuery = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const sendQuery = useCallback(async (query) => {
    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: query,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.sendQuery(query);

      // Add AI response
      const aiMessage = {
        id: response.message_id || Date.now() + 1,
        type: 'ai',
        content: response.content,
        metadata: response.metadata,
        timestamp: new Date(response.timestamp)
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (err) {
      console.error('Query error:', err);
      setError(err.message);

      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: {
          text: `Error: ${err.response?.data?.detail || err.message || 'Failed to process query'}`,
          visualizations: []
        },
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    sendQuery,
    clearMessages,
    isLoading,
    error
  };
};
