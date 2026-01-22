import React from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import TimelineViz from '../Visualizations/TimelineViz';
import NetworkGraph from '../Visualizations/NetworkGraph';
import BarChart from '../Visualizations/BarChart';
import LineChart from '../Visualizations/LineChart';
import SankeyDiagram from '../Visualizations/SankeyDiagram';
import ChoroplethMap from '../Visualizations/ChoroplethMap';
import Heatmap from '../Visualizations/Heatmap';
import ForceDirectedGraph from '../Visualizations/ForceDirectedGraph';

const MessageCard = ({ message }) => {
  const isUser = message.type === 'user';
  const isError = message.type === 'error';

  if (isUser) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Paper
          sx={{
            p: 2,
            maxWidth: '70%',
            bgcolor: 'primary.main',
            color: 'primary.contrastText'
          }}
        >
          <Typography variant="body1">{message.content}</Typography>
        </Paper>
      </Box>
    );
  }

  const content = message.content;
  const text = content.text || '';
  const visualizations = content.visualizations || [];

  return (
    <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
      <Paper
        sx={{
          p: 3,
          maxWidth: '90%',
          width: '100%',
          bgcolor: isError ? 'error.light' : 'background.paper'
        }}
      >
        {/* Text Content */}
        {text && (
          <Box sx={{ mb: visualizations.length > 0 ? 3 : 0 }}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ children }) => (
                  <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
                    {children}
                  </Typography>
                ),
                h2: ({ children }) => (
                  <Typography variant="h5" gutterBottom sx={{ mt: 3, fontWeight: 600 }}>
                    {children}
                  </Typography>
                ),
                h3: ({ children }) => (
                  <Typography variant="h6" gutterBottom sx={{ mt: 2, fontWeight: 600 }}>
                    {children}
                  </Typography>
                ),
                p: ({ children }) => (
                  <Typography variant="body1" paragraph>
                    {children}
                  </Typography>
                ),
                li: ({ children }) => (
                  <Typography component="li" variant="body1" sx={{ ml: 2, mb: 0.5 }}>
                    {children}
                  </Typography>
                ),
              }}
            >
              {text}
            </ReactMarkdown>
          </Box>
        )}

        {/* Visualizations */}
        {visualizations.map((viz) => (
          <Box key={viz.id} sx={{ mb: 3 }}>
            {viz.title && (
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                {viz.title}
              </Typography>
            )}

            {viz.type === 'timeline' && <TimelineViz data={viz.data} />}
            {viz.type === 'network_graph' && <NetworkGraph data={viz.data} />}
            {viz.type === 'bar_chart' && <BarChart data={viz.data} />}
            {viz.type === 'line_chart' && <LineChart data={viz.data} />}
            {viz.type === 'sankey_diagram' && <SankeyDiagram data={viz.data} />}
            {viz.type === 'choropleth_map' && <ChoroplethMap data={viz.data} />}
            {viz.type === 'heatmap' && <Heatmap data={viz.data} />}
            {viz.type === 'force_directed_graph' && <ForceDirectedGraph data={viz.data} />}

            {/* Fallback for unknown types */}
            {!['timeline', 'network_graph', 'bar_chart', 'line_chart', 'sankey_diagram', 'choropleth_map', 'heatmap', 'force_directed_graph'].includes(viz.type) && (
              <Typography variant="body2" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                Visualization type "{viz.type}" is not yet implemented in the frontend.
              </Typography>
            )}
          </Box>
        ))}

        {/* Metadata */}
        {message.metadata && (
          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="caption" color="text.secondary">
              {message.metadata.data_points} data points •{' '}
              {message.metadata.visualizations_count} visualizations
            </Typography>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default MessageCard;
