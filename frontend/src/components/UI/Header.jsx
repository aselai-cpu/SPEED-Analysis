import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import AccountTreeIcon from '@mui/icons-material/AccountTree';

const Header = ({ onMenuClick }) => {
  return (
    <AppBar position="static">
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <AccountTreeIcon sx={{ mr: 2 }} />

        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          SPEED Knowledge Graph Query
        </Typography>

        <Typography variant="body2" sx={{ opacity: 0.8 }}>
          AI-Powered Analysis
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
