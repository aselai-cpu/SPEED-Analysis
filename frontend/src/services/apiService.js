import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Send a query
  async sendQuery(query) {
    const response = await apiClient.post('/api/query', { query });
    return response.data;
  },

  // Get example queries
  async getExamples() {
    const response = await apiClient.get('/api/examples');
    return response.data;
  },

  // Health check
  async healthCheck() {
    const response = await apiClient.get('/api/health');
    return response.data;
  },
};

export default apiService;
