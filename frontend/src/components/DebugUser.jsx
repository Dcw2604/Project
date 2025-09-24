import React from 'react';
import { Typography, Paper, Button } from '@mui/material';
import { useAuth } from '../hooks/useAuth';

const DebugUser = () => {
  const { user, isAuthenticated, clearCache } = useAuth();

  return (
    <Paper sx={{ p: 2, m: 2, backgroundColor: 'rgba(255,255,255,0.1)' }}>
      <Typography variant="h6" color="white">Debug Info:</Typography>
      <Typography color="white">Is Authenticated: {isAuthenticated ? 'Yes' : 'No'}</Typography>
      <Typography color="white">User: {user ? JSON.stringify(user, null, 2) : 'null'}</Typography>
      <Typography color="white">User Role: '{user?.role || 'undefined'}'</Typography>
      <Typography color="white">Role Type: {typeof user?.role}</Typography>
      <Typography color="white">Is Student: {user?.role === 'student' ? 'Yes' : 'No'}</Typography>
      <Button 
        variant="contained" 
        color="secondary" 
        onClick={clearCache}
        sx={{ mt: 1 }}
      >
        Clear Cache & Re-login
      </Button>
    </Paper>
  );
};

export default DebugUser;
