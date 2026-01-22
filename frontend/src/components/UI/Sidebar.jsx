import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Divider from '@mui/material/Divider';
import Chip from '@mui/material/Chip';
import apiService from '../../services/apiService';

const Sidebar = () => {
  const [examples, setExamples] = useState([]);

  useEffect(() => {
    loadExamples();
  }, []);

  const loadExamples = async () => {
    try {
      const data = await apiService.getExamples();
      setExamples(data.categories || []);
    } catch (error) {
      console.error('Failed to load examples:', error);
    }
  };

  return (
    <Box
      sx={{
        width: 320,
        bgcolor: 'background.paper',
        borderRight: 1,
        borderColor: 'divider',
        overflowY: 'auto',
        p: 2
      }}
    >
      <Typography variant="h6" gutterBottom>
        Example Queries
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Click to try these questions
      </Typography>

      {examples.map((category, idx) => (
        <Box key={idx} sx={{ mb: 2 }}>
          <Chip
            label={category.category}
            size="small"
            color="primary"
            variant="outlined"
            sx={{ mb: 1 }}
          />

          <List dense>
            {category.queries.map((query, qIdx) => (
              <ListItem key={qIdx} disablePadding>
                <ListItemButton
                  onClick={() => {
                    // Dispatch custom event to send query
                    window.dispatchEvent(
                      new CustomEvent('example-query', { detail: query })
                    );
                  }}
                >
                  <ListItemText
                    primary={query}
                    primaryTypographyProps={{
                      variant: 'body2',
                      sx: { fontSize: '0.875rem' }
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>

          {idx < examples.length - 1 && <Divider sx={{ my: 1 }} />}
        </Box>
      ))}
    </Box>
  );
};

export default Sidebar;
