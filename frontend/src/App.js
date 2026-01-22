import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import ChatInterface from './components/ChatInterface/ChatInterface';
import Header from './components/UI/Header';
import Sidebar from './components/UI/Sidebar';
import './App.css';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          {sidebarOpen && <Sidebar />}
          <ChatInterface />
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
